import os
import sys
import json
import logging

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import config
from src.gmail_service import authenticate, get_gmail_service, fetch_unread_emails, get_email_details, mark_emails_as_read
from src.sheets_service import get_sheets_service, append_to_sheet
from src.email_parser import parse_email

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('app.log')
    ]
)
logger = logging.getLogger(__name__)

def load_processed_ids():
    if not os.path.exists(config.STATE_FILE):
        return set()
    try:
        with open(config.STATE_FILE, 'r') as f:
            data = json.load(f)
            return set(data.get('processed_ids', []))
    except Exception as e:
        logger.error(f"Error loading state: {e}")
        return set()

def save_processed_ids(processed_ids):
    try:
        with open(config.STATE_FILE, 'w') as f:
            json.dump({'processed_ids': list(processed_ids)}, f)
    except Exception as e:
        logger.error(f"Error saving state: {e}")

def main():
    logger.info("Starting Gmail to Sheets automation...")
    
    try:
        creds = authenticate(config.CREDENTIALS_FILE, config.TOKEN_FILE, config.SCOPES)
    except Exception as e:
        logger.critical(f"Authentication failed: {e}")
        return

    gmail_service = get_gmail_service(creds)
    sheets_service = get_sheets_service(creds)
    
    logger.info("Fetching unread emails...")
    messages = fetch_unread_emails(gmail_service)
    if not messages:
        logger.info("No unread emails found.")
        return

    logger.info(f"Found {len(messages)} unread messages.")
    
    processed_ids = load_processed_ids()
    new_rows = []
    ids_to_mark_read = []
    
    for message_summary in messages:
        msg_id = message_summary['id']
        
        if msg_id in processed_ids:
            logger.info(f"Skipping duplicate email ID: {msg_id}")
            ids_to_mark_read.append(msg_id)
            continue
            
        try:
            msg_detail = get_email_details(gmail_service, msg_id)
            parsed_email = parse_email(msg_detail)
            
            row = [
                parsed_email['from'],
                parsed_email['subject'],
                parsed_email['date'],
                parsed_email['content']
            ]
            new_rows.append(row)
            ids_to_mark_read.append(msg_id)
            processed_ids.add(msg_id)
            
        except Exception as e:
            logger.error(f"Error processing message {msg_id}: {e}")
    
    if new_rows:
        logger.info(f"Appending {len(new_rows)} rows to Google Sheets...")
        try:
            append_to_sheet(sheets_service, config.SPREADSHEET_ID, config.RANGE_NAME, new_rows)
            
            logger.info("Marking emails as read...")
            mark_emails_as_read(gmail_service, ids_to_mark_read)
            
            logger.info("Saving state...")
            save_processed_ids(processed_ids)
            
            logger.info("Batch processing complete.")
            
        except Exception as e:
            logger.error(f"Failed to write to Sheets: {e}")
    else:
        logger.info("No new emails to process matching criteria.")
        if ids_to_mark_read:
             logger.info(f"Marking {len(ids_to_mark_read)} previously processed emails as read.")
             mark_emails_as_read(gmail_service, ids_to_mark_read)

if __name__ == '__main__':
    main()