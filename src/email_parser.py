import base64
from bs4 import BeautifulSoup
from dateutil import parser as date_parser

def clean_text(text): #to clean whitespaces
    if text:
        return " ".join(text.split())
    return ""

def get_header_value(headers, name): #to extract email header
    for header in headers:
        if header['name'].lower() == name.lower():
            return header['value']
    return ""

def parse_message_body(payload): #to extract email body
    body = ""
    if 'parts' in payload:
        for part in payload['parts']:
            if part['mimeType'] == 'text/plain':
                data = part['body'].get('data')
                if data:
                    body += base64.urlsafe_b64decode(data).decode('utf-8')
            elif part['mimeType'] == 'text/html':
                pass
            elif 'parts' in part:
                body += parse_message_body(part)
    
    if not body and payload.get('body') and payload['body'].get('data'):
         body = base64.urlsafe_b64decode(payload['body']['data']).decode('utf-8')
    
    if not body:
         if 'parts' in payload:
            for part in payload['parts']:
                if part['mimeType'] == 'text/html':
                    data = part['body'].get('data')
                    if data:
                        html = base64.urlsafe_b64decode(data).decode('utf-8')
                        soup = BeautifulSoup(html, 'html.parser')
                        body = soup.get_text()
    
    return clean_text(body)

def parse_email(message): #to combine everything
    payload = message.get('payload', {})
    headers = payload.get('headers', [])
    
    email_data = {
        'id': message['id'],
        'from': get_header_value(headers, 'From'),
        'subject': get_header_value(headers, 'Subject'),
        'date': get_header_value(headers, 'Date'),
        'content': parse_message_body(payload)
    }
    
    try:
        dt = date_parser.parse(email_data['date'])
        email_data['date'] = dt.strftime('%Y-%m-%d %H:%M:%S')
    except:
        pass 
        
    return email_data