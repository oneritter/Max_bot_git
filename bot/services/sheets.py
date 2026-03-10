import gspread
from google.oauth2.service_account import Credentials
from config import GOOGLE_SHEETS_CREDENTIALS_FILE, GOOGLE_SHEETS_SPREADSHEET_ID, GOOGLE_SHEETS_SHEET_NAME

_client = None


def _get_sheet():
    global _client
    if _client is None:
        creds = Credentials.from_service_account_file(
            GOOGLE_SHEETS_CREDENTIALS_FILE,
            scopes=["https://www.googleapis.com/auth/spreadsheets"]
        )
        _client = gspread.authorize(creds)
    spreadsheet = _client.open_by_key(GOOGLE_SHEETS_SPREADSHEET_ID)
    return spreadsheet.worksheet(GOOGLE_SHEETS_SHEET_NAME)


def append_training_request(partner_name: str, surname: str, phone: str, topic: str, date: str, time: str):
    sheet = _get_sheet()
    sheet.append_row([partner_name, surname, phone, topic, date, time])
