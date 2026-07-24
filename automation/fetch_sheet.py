import gspread
from google.oauth2.service_account import Credentials

from automation.parser import parse_row

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets.readonly"
]

SHEET_ID = "1QSCmUtzvALYFr16MD2lrXv1HdtHbZV46ET9GivBrqVI"


def fetch_updates():

    creds = Credentials.from_service_account_file(
        "credentials.json",
        scopes=SCOPES
    )

    client = gspread.authorize(creds)

    spreadsheet = client.open_by_key(SHEET_ID)

    worksheet = spreadsheet.sheet1

    rows = worksheet.get_all_records()

    updates = []

    for row in rows:
        cleaned = {}

        for key, value in row.items():
            cleaned[key.strip()] = value 

        updates.append(parse_row(cleaned))

    return updates