import os.path
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# نطاق القراءة فقط
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

def gmail_login_and_fetch(user_id='me', max_results=100, filter_senders=None):
    """
    تسجيل الدخول إلى Gmail وجلب الرسائل مع خيار الفلترة حسب المرسل.
    Args:
        user_id: المستخدم، عادةً 'me'
        max_results: الحد الأقصى لعدد الرسائل
        filter_senders: قائمة كلمات أو أسماء مرسلين لتصفية النتائج
    Returns:
        قائمة من الرسائل مفلترة
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
        hdr_dict = {h['name']: h['value'] for h in headers}
        sender = hdr_dict.get('From', '')

        if filter_senders:
            if not any(f.lower() in sender.lower() for f in filter_senders):
                continue

        fetched.append({
            'id': msg['id'],
            'threadId': m.get('threadId'),
            'snippet': m.get('snippet'),
            'headers': headers
        })

    return fetched
