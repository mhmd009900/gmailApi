import os.path
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# إذا أردت فقط قراءة الرسائل:
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

def gmail_login_and_fetch(user_id='me', max_results=10):
    """
    يفتح صلاحيات Gmail API ثم يستدعي رسائل البريد.
    Args:
      user_id: 'me' للإيميل المرتبط بالـ OAuth token.
      max_results: عدد الرسائل الأقصى لكل جلب.
    Returns:
      قائمة من dicts تحوي id وعنوان كل رسالة وSnippet.
    """
    creds = None
    # عند أول تشغيل، سيُنشئ token.json
    if os.path.exists('token2.json'):
        creds = Credentials.from_authorized_user_file('token2.json', SCOPES)
    # إذا انتهت صلاحيات token أو لا يوجد:
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials2.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # حفظ التوكن لاستخدام لاحق
        with open('token2.json', 'w') as token:
            token.write(creds.to_json())

    # إنشاء الخدمة
    service = build('gmail', 'v1', credentials=creds)
    # جلب لائحة بالرسائل
    results = service.users().messages().list(
        userId=user_id,
        maxResults=max_results
    ).execute()
    messages = results.get('messages', [])

    fetched = []
    for msg in messages:
        m = service.users().messages().get(
            userId=user_id,
            id=msg['id'],
            format='metadata',
            metadataHeaders=['Subject','From','Date']
        ).execute()
        fetched.append({
            'id': msg['id'],
            'threadId': m.get('threadId'),
            'snippet': m.get('snippet'),
            'headers': m.get('payload',{}).get('headers',[])
        })
    return fetched

if __name__ == '__main__':
    msgs = gmail_login_and_fetch(max_results=10)
    for m in msgs:
        # استخراج العنوان والمرسل
        hdrs = {h['name']: h['value'] for h in m['headers']}
        print(f"From: {hdrs.get('From')} | Subject: {hdrs.get('Subject')} | Date: {hdrs.get('Date')}")
        print("Snippet:", m['snippet'])
        print("-" * 50)
