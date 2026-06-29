import gspread
from oauth2client.service_account import ServiceAccountCredentials
from dotenv import load_dotenv
import os
import json

load_dotenv()

def get_sheet():
    import json
    scope = [
        "https://spreadsheets.google.com/feeds",
        "https://www.googleapis.com/auth/drive"
    ]

    # Try environment variable first (for cloud deployment)
    creds_json = os.getenv("GOOGLE_CREDENTIALS_JSON")
    if creds_json:
        creds_dict = json.loads(creds_json)
        creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
    else:
        # Fall back to local file (for local development)
        creds = ServiceAccountCredentials.from_json_keyfile_name("briefcase-credentials.json", scope)

    client = gspread.authorize(creds)
    sheet_id = os.getenv("GOOGLE_SHEET_ID")
    return client.open_by_key(sheet_id).sheet1

try:
    sheet=get_sheet()
    records=sheet.get_all_records()
    print("Connected to Google Sheets!")
    print(f'Found {len(records)} advisors:')
    for r in records:
        print(f' - {r.get('name')} ({r.get('email')})')
except Exception as e:
    import traceback
    print(f'Error type: {type(e).__name__}')
    print(f'Error: {str(e)}')
    traceback.print_exc()