from fastapi import FastAPI, Query
from typing import List, Optional
from gmail_reader import gmail_login_and_fetch

app = FastAPI(
    title="Gmail Reader API",
    description="API لجلب رسائل Gmail مع إمكانية فلترة المرسلين مثل (Facebook, Twitter...)",
    version="1.0"
)

@app.get("/emails")
def get_emails(
    max_results: int = 50,
    filter_senders: Optional[List[str]] = Query(default=None, description="فلترة حسب كلمات أو أسماء مرسلين")
):
    emails = gmail_login_and_fetch(max_results=max_results, filter_senders=filter_senders)
    output = []
    for m in emails:
        hdrs = {h['name']: h['value'] for h in m['headers']}
        output.append({
            "from": hdrs.get("From"),
            "subject": hdrs.get("Subject"),
            "date": hdrs.get("Date"),
            "snippet": m["snippet"]
        })
    return output
