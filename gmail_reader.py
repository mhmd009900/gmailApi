import os.path
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

def gmail_fetch_filtered_confirmations(user_id='me', filter_senders=None):
    creds = None
    if os.path.exists('token2.json'):
        creds = Credentials.from_authorized_user_file('token2.json', SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('credentials2.json', SCOPES)
            creds = flow.run_local_server(port=0)
        with open('token2.json', 'w') as token:
            token.write(creds.to_json())

    service = build('gmail', 'v1', credentials=creds)
    results = service.users().messages().list(userId=user_id, maxResults=20).execute()
    messages = results.get('messages', [])

    matched = []
    for msg in messages:
        m = service.users().messages().get(
            userId=user_id,
            id=msg['id'],
            format='metadata',
            metadataHeaders=['Subject', 'From', 'Date']
        ).execute()

        headers = m.get('payload', {}).get('headers', [])
        hdrs = {h['name']: h['value'] for h in headers}
        subject = hdrs.get('Subject', '')
        sender = hdrs.get('From', '')
        snippet = m.get('snippet', '')

        # تحقق من وجود "confirmation code" في الموضوع أو المقطع
        if "confirmation code" not in (subject + snippet).lower():
            continue

        # فلترة المرسل إذا تم تحديدها
        if filter_senders:
            found = False
            for keyword in filter_senders:
                if keyword.lower() in sender.lower() and "registration" in sender.lower():
                    found = True
                    break
            if not found:
                continue

        matched.append({
            "from": sender,
            "subject": subject,
            "date": hdrs.get("Date"),
            "snippet": snippet
        })

    return matched
