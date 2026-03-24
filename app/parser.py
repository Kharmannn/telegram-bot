import re
from datetime import datetime


def parse_input(text: str) -> dict | None:
    """
    Format yang diterima:
      rokok 31500
      rokok kaki lima 31500
      25/03/2026 rokok 31500
      25/03/2026 rokok kaki lima 31500
    """
    pattern = r"^(?:(\d{1,2}/\d{1,2}/\d{4})\s+)?(.+?)\s+(\d+(?:[.,]\d+)?)$"
    match = re.match(pattern, text.strip())
    if not match:
        return None

    raw_date   = match.group(1)
    deskripsi  = match.group(2).strip()
    raw_nominal = match.group(3).replace(",", ".")

    try:
        nominal = float(raw_nominal)
    except ValueError:
        return None

    if not deskripsi or nominal <= 0:
        return None

    # Parse tanggal
    if raw_date:
        tanggal = parse_date(raw_date)
        if not tanggal:
            return None
    else:
        tanggal = datetime.now().strftime("%d/%m/%Y")

    return {
        "tanggal" : tanggal,
        "deskripsi": deskripsi,
        "nominal"  : nominal,
    }


def parse_date(date_str: str) -> str | None:
    """Validasi dan normalisasi tanggal dd/mm/yyyy."""
    parts = date_str.split("/")
    if len(parts) != 3:
        return None
    try:
        d, m, y = int(parts[0]), int(parts[1]), int(parts[2])
        dt = datetime(y, m, d)
        return dt.strftime("%d/%m/%Y")
    except ValueError:
        return None