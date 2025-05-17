from fastapi import FastAPI, Query
from typing import List, Optional
from gmail_reader import gmail_login_and_fetch

app = FastAPI()

@app.get("/emails")
def get_emails(
    filter_senders: Optional[List[str]] = Query(default=None),
    confirmation_only: Optional[bool] = True
):
    emails = gmail_login_and_fetch(
        max_results=20,
        filter_senders=filter_senders,
        confirmation_only=confirmation_only
    )

    output = []
    for m in emails:
        hdrs = {h['name']: h['value'] for h in m['headers']}
        output.append({
            
            "subject": hdrs.get("Subject"),
            "date": hdrs.get("Date"),
            
        })

    return output
