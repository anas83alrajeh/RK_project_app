import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd

SCOPE = ["https://spreadsheets.google.com/feeds",
         "https://www.googleapis.com/auth/drive"]

CREDENTIALS_FILE = "credentials.json"
SPREADSHEET_NAME = "app"

def get_gsheet_client():
    creds = ServiceAccountCredentials.from_json_keyfile_name(CREDENTIALS_FILE, SCOPE)
    client = gspread.authorize(creds)
    return client

def load_df(sheet_name, worksheet_name):
    client = get_gsheet_client()
    sheet = client.open(sheet_name)
    try:
        worksheet = sheet.worksheet(worksheet_name)
        data = worksheet.get_all_records()
        if data:
            return pd.DataFrame(data)
        else:
            return pd.DataFrame()
    except gspread.WorksheetNotFound:
        return pd.DataFrame()

def save_df(df, sheet_name, worksheet_name):
    client = get_gsheet_client()
    sheet = client.open(sheet_name)
    try:
        worksheet = sheet.worksheet(worksheet_name)
        worksheet.clear()
    except gspread.WorksheetNotFound:
        worksheet = sheet.add_worksheet(title=worksheet_name, rows="1000", cols="20")
    worksheet.update([df.columns.values.tolist()] + df.values.tolist())
