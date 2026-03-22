import os
import logging
from datetime import datetime
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build

logger = logging.getLogger(__name__)

SPREADSHEET_ID  = os.environ["SPREADSHEET_ID"]
CREDENTIALS_PATH = os.environ.get("CREDENTIALS_PATH", "/credentials/service_account.json")

SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]

MONTHS = ["jan","feb","mar","apr","mei","jun","jul","agt","sep","okt","nov","des"]

def get_service():
    creds = Credentials.from_service_account_file(CREDENTIALS_PATH, scopes=SCOPES)
    service = build("sheets", "v4", credentials=creds, cache_discovery=False)
    return service

def sheet_name_from_date(tanggal: str) -> str:
    """21/03/2026 → mar_2026"""
    parts = tanggal.split("/")
    month = int(parts[1]) - 1
    year  = parts[2]
    return f"{MONTHS[month]}_{year}"

def ensure_sheet_exists(service, sheet_name: str):
    """Buat tab baru kalau belum ada, lengkap dengan header."""
    spreadsheet = service.spreadsheets().get(spreadsheetId=SPREADSHEET_ID).execute()
    existing    = [s["properties"]["title"] for s in spreadsheet["sheets"]]

    if sheet_name not in existing:
        body = {
            "requests": [{
                "addSheet": {
                    "properties": {"title": sheet_name}
                }
            }]
        }
        service.spreadsheets().batchUpdate(
            spreadsheetId=SPREADSHEET_ID,
            body=body
        ).execute()
        logger.info(f"Sheet baru dibuat: {sheet_name}")

        # Tulis header
        service.spreadsheets().values().update(
            spreadsheetId=SPREADSHEET_ID,
            range=f"{sheet_name}!A1:C1",
            valueInputOption="RAW",
            body={"values": [["Tanggal", "Deskripsi", "Nominal"]]}
        ).execute()

def is_date_exists(service, sheet_name: str, tanggal: str) -> bool:
    """Cek apakah tanggal sudah ada di kolom A."""
    try:
        result = service.spreadsheets().values().get(
            spreadsheetId=SPREADSHEET_ID,
            range=f"{sheet_name}!A:A"
        ).execute()
        values = result.get("values", [])
        for row in values:
            if row and row[0] == tanggal:
                return True
        return False
    except Exception:
        return False

import time

def append_to_sheet(tanggal: str, deskripsi: str, nominal: float) -> str:
    for attempt in range(3):  # retry 3x
        try:
            service    = get_service()
            sheet_name = sheet_name_from_date(tanggal)
            ensure_sheet_exists(service, sheet_name)
            tanggal_exists = is_date_exists(service, sheet_name, tanggal)
            tanggal_cell   = "" if tanggal_exists else tanggal
            row = [tanggal_cell, deskripsi, int(nominal)]
            service.spreadsheets().values().append(
                spreadsheetId=SPREADSHEET_ID,
                range=f"{sheet_name}!A:C",
                valueInputOption="USER_ENTERED",
                insertDataOption="INSERT_ROWS",
                body={"values": [row]}
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
