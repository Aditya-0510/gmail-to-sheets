import os

SCOPES = [
    'https://www.googleapis.com/auth/gmail.readonly',
    'https://www.googleapis.com/auth/gmail.modify', 
    'https://www.googleapis.com/auth/spreadsheets'
]

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CREDENTIALS_FILE = os.path.join(BASE_DIR, 'credentials', 'credentials.json')
TOKEN_FILE = os.path.join(BASE_DIR, 'credentials', 'token.json')
STATE_FILE = os.path.join(BASE_DIR, 'start_history.json')

SPREADSHEET_ID = '1w9ki_BynQDBVVcmuQHZntQm1XNtgs9hYpP7jyN2yOFk' 
RANGE_NAME = 'Sheet1!A:D' 