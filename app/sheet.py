import os
import logging
import time
import base64
import json
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build

logger = logging.getLogger(__name__)

SPREADSHEET_ID   = os.environ["SPREADSHEET_ID"]
CREDENTIALS_PATH = os.environ.get("CREDENTIALS_PATH", "/credentials/service_account.json")

# Owner: kolom A-B-C, Member: kolom E-F-G
OWNER_IDS  = list(map(int, os.environ.get("ALLOWED_IDS", "").split(","))) if os.environ.get("ALLOWED_IDS") else []
MEMBER_IDS = list(map(int, os.environ.get("MEMBER_IDS", "").split(",")))  if os.environ.get("MEMBER_IDS")  else []

COL_OWNER  = 0  # A=0, B=1, C=2
COL_MEMBER = 4  # E=4, F=5, G=6

SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]
MONTHS = ["jan","feb","mar","apr","mei","jun","jul","agt","sep","okt","nov","des"]


def col_letter(idx: int) -> str:
    return chr(ord('A') + idx)


def get_service():
    creds_b64 = os.environ.get("GOOGLE_CREDENTIALS_B64")
    if creds_b64:
        creds_json = json.loads(base64.b64decode(creds_b64).decode("utf-8"))
        creds = Credentials.from_service_account_info(creds_json, scopes=SCOPES)
    else:
        creds = Credentials.from_service_account_file(CREDENTIALS_PATH, scopes=SCOPES)
    return build("sheets", "v4", credentials=creds, cache_discovery=False)


def sheet_name_from_date(tanggal: str) -> str:
    """21/03/2026 → mar_2026"""
    parts = tanggal.split("/")
    month = int(parts[1]) - 1
    year  = parts[2]
    return f"{MONTHS[month]}_{year}"


def get_col_start(chat_id: int) -> int:
    """Return kolom start index berdasarkan chat_id."""
    if chat_id in MEMBER_IDS:
        return COL_MEMBER  # E
    return COL_OWNER       # A


def get_total_expenditure(tanggal: str, chat_id: int) -> int:
    """Hitung total nominal di sheet bulan ini untuk user tertentu."""
    try:
        service     = get_service()
        sheet_name  = sheet_name_from_date(tanggal)
        col_start   = get_col_start(chat_id)
        nominal_col = col_letter(col_start + 2)  # C untuk owner, G untuk member

        result = service.spreadsheets().values().get(
            spreadsheetId=SPREADSHEET_ID,
            range=f"{sheet_name}!{nominal_col}2:{nominal_col}1000"  # skip header row 1
        ).execute()

        values = result.get("values", [])
        total  = 0
        for row in values:
            if row and row[0].strip():
                try:
                    total += int(float(str(row[0]).replace(",", "")))
                except ValueError:
                    pass
        return total
    except Exception as e:
        logger.warning(f"get_total_expenditure error: {e}")
        return 0


def ensure_sheet_exists(service, sheet_name: str):
    """Buat tab baru kalau belum ada, lengkap dengan header A-C dan E-G."""
    spreadsheet = service.spreadsheets().get(spreadsheetId=SPREADSHEET_ID).execute()
    existing    = [s["properties"]["title"] for s in spreadsheet["sheets"]]

    if sheet_name not in existing:
        service.spreadsheets().batchUpdate(
            spreadsheetId=SPREADSHEET_ID,
            body={"requests": [{"addSheet": {"properties": {"title": sheet_name}}}]}
        ).execute()
        logger.info(f"Sheet baru dibuat: {sheet_name}")

        service.spreadsheets().values().batchUpdate(
            spreadsheetId=SPREADSHEET_ID,
            body={
                "valueInputOption": "RAW",
                "data": [
                    {"range": f"{sheet_name}!A1:C1", "values": [["Tanggal", "Deskripsi", "Nominal"]]},
                    {"range": f"{sheet_name}!E1:G1", "values": [["Tanggal", "Deskripsi", "Nominal"]]},
                ]
            }
        ).execute()


def is_date_exists_in_col(service, sheet_name: str, tanggal: str, col_start: int) -> bool:
    """Cek apakah tanggal sudah ada di kolom tanggal (col_start)."""
    col = col_letter(col_start)
    try:
        result = service.spreadsheets().values().get(
            spreadsheetId=SPREADSHEET_ID,
            range=f"{sheet_name}!{col}:{col}"
        ).execute()
        values = result.get("values", [])
        for row in values:
            if row and row[0] == tanggal:
                return True
        return False
    except Exception:
        return False


def get_last_row_for_col(service, sheet_name: str, col_start: int) -> int:
    """Cari baris terakhir yang terisi di kolom deskripsi (col_start+1)."""
    col = col_letter(col_start + 1)
    try:
        result = service.spreadsheets().values().get(
            spreadsheetId=SPREADSHEET_ID,
            range=f"{sheet_name}!{col}:{col}"
        ).execute()
        values = result.get("values", [])
        # Minimal row 2 (row 1 = header)
        return max(len(values) + 1, 2)
    except Exception:
        return 2


def append_to_sheet(tanggal: str, deskripsi: str, nominal: float, chat_id: int) -> str:
    for attempt in range(3):
        try:
            service    = get_service()
            sheet_name = sheet_name_from_date(tanggal)
            col_start  = get_col_start(chat_id)

            ensure_sheet_exists(service, sheet_name)

            tanggal_exists = is_date_exists_in_col(service, sheet_name, tanggal, col_start)
            tanggal_cell   = "" if tanggal_exists else tanggal
            next_row       = get_last_row_for_col(service, sheet_name, col_start)

            c1 = col_letter(col_start)
            c2 = col_letter(col_start + 2)

            service.spreadsheets().values().update(
                spreadsheetId=SPREADSHEET_ID,
                range=f"{sheet_name}!{c1}{next_row}:{c2}{next_row}",
                valueInputOption="USER_ENTERED",
                body={"values": [[tanggal_cell, deskripsi, int(nominal)]]}
            ).execute()

            if tanggal_exists:
                return f"Sheet: {sheet_name} | Ditambah ke {tanggal}"
            else:
                return f"Sheet: {sheet_name} | Tanggal baru: {tanggal}"

        except Exception as e:
            logger.warning(f"Attempt {attempt+1} failed: {e}")
            if attempt < 2:
                time.sleep(2)
            else:
                raise