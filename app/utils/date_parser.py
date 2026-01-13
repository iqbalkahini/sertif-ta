MONTH_MAP = {
    "januari": "01", "februari": "02", "maret": "03", "april": "04",
    "mei": "05", "juni": "06", "juli": "07", "agustus": "08",
    "september": "09", "oktober": "10", "november": "11", "desember": "12"
}

def parse_indonesian_date(date_str: str) -> str:
    """
    Convert Indonesian date format to dd-mm-yyyy.
    Example: '1 Juli 2024' -> '01-07-2024'
    """
    try:
        parts = date_str.strip().split()
        if len(parts) >= 3:
            day = parts[0].zfill(2)
            month = MONTH_MAP.get(parts[1].lower(), "00")
            year = parts[2]
            return f"{day}-{month}-{year}"
    except Exception:
        pass
    # Fallback: replace spaces with dashes
    return date_str.replace(" ", "-").replace("/", "-")
