import os
import base64
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

def authenticate_gmail():
    creds = None

    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(
                port=8000,
                access_type='offline',  # <--- Request refresh token
                prompt='consent'        # <--- Force consent screen every time for refresh token
            )

        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    service = build('gmail', 'v1', credentials=creds)
    return service



def fetch_latest_unread_emails(service, max_results=10):
    results = service.users().messages().list(userId='me', labelIds=['INBOX', 'UNREAD'], maxResults=max_results).execute()
    messages = results.get('messages', [])

    emails = []
    for msg in messages:
        msg_data = service.users().messages().get(userId='me', id=msg['id'], format='full').execute()

        payload = msg_data['payload']
        headers = {h['name']: h['value'] for h in payload['headers']}
        subject = headers.get('Subject', '')
        sender = headers.get('From', '')
        date = headers.get('Date', '')

        parts = payload.get('parts', [])
        body = ""
        if parts:
            for part in parts:
                if part['mimeType'] == 'text/plain':
                    data = part['body'].get('data')
                    if data:
                        body = base64.urlsafe_b64decode(data).decode('utf-8')
        else:
            data = payload['body'].get('data')
            if data:
                body = base64.urlsafe_b64decode(data).decode('utf-8')

        emails.append({
            'id': msg['id'],
            'subject': subject,
            'from': sender,
            'date': date,
            'body': body
        })

    return emails
