import os.path
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from typing import Optional, List

SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

def gmail_login_and_fetch(
    user_id: str = 'me',
    max_results: int = 20,
    filter_senders: Optional[List[str]] = None,
    confirmation_only: Optional[bool] = True
):
    """
    يجلب رسائل Gmail مع دعم الفلاتر:
    - filter_senders: كلمات يجب أن تكون في عنوان المرسل (From)
    - confirmation_only: فلترة الرسائل التي تحتوي على "confirmation code"
    """
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
    results = service.users().messages().list(userId=user_id, maxResults=max_results).execute()
    messages = results.get('messages', [])

    fetched = []
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

        # إذا كان مطلوبًا التأكد من وجود "confirmation code"
        if confirmation_only:
            if "confirmation code" not in (subject + snippet).lower():
                continue

        # إذا تم تحديد فلترة للمرسلين
        if filter_senders:
            found = False
            for keyword in filter_senders:
                if keyword.lower() in sender.lower() and "registration" in sender.lower():
                    found = True
                    break
            if not found:
                continue

        fetched.append({
            'id': msg['id'],
            'threadId': m.get('threadId'),
            'snippet': snippet,
            'headers': headers
        })

    return fetched
