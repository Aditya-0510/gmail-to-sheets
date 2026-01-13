import os.path
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

def authenticate(credentials_file, token_file, scopes):
    creds = None
    if os.path.exists(token_file):
        creds = Credentials.from_authorized_user_file(token_file, scopes)
    
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if not os.path.exists(credentials_file):
                raise FileNotFoundError(f"Credentials file not found at {credentials_file}")
            
            flow = InstalledAppFlow.from_client_secrets_file(
                credentials_file, scopes)
            creds = flow.run_local_server(port=0)
            
        with open(token_file, 'w') as token:
            token.write(creds.to_json())
            
    return creds

def get_gmail_service(creds): #to create a gmail api client
    return build('gmail', 'v1', credentials=creds)

def fetch_unread_emails(service, max_results=50): #to fetch unread emails
    query = 'label:INBOX is:unread'
    results = service.users().messages().list(userId='me', q=query, maxResults=max_results).execute()
    messages = results.get('messages', [])
    return messages

def get_email_details(service, msg_id): #to fetch eamil data
    message = service.users().messages().get(userId='me', id=msg_id, format='full').execute()
    return message

def mark_emails_as_read(service, msg_ids): #to mark emails as read
    if not msg_ids:
        return
        
    batch_request = {
        'ids': msg_ids,
        'removeLabelIds': ['UNREAD']
    }
    service.users().messages().batchModify(userId='me', body=batch_request).execute()