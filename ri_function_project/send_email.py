import os
import requests
import base64

def send_email_with_csv(csv_content: bytes, recipient_email: str):
    SENDGRID_API_KEY = os.getenv("SENDGRID_API_KEY")
    SENDER_EMAIL = os.getenv("SENDER_EMAIL")

    if not SENDGRID_API_KEY or not SENDER_EMAIL:
        raise EnvironmentError("Missing SENDGRID_API_KEY or SENDER_EMAIL in environment variables")

    # Encode CSV content to base64
    encoded_file = base64.b64encode(csv_content).decode()

    email_data = {
        "personalizations": [
            {
                "to": [{"email": recipient_email}],
                "subject": "RI/SP Recommendation Report"
            }
        ],
        "from": {"email": SENDER_EMAIL},
        "content": [
            {
                "type": "text/plain",
                "value": "Attached is the latest RI/SP recommendation report."
            }
        ],
        "attachments": [
            {
                "content": encoded_file,
                "type": "text/csv",
                "filename": "ri_sp_report.csv",
                "disposition": "attachment"
            }
        ]
    }

    response = requests.post(
        url="https://api.sendgrid.com/v3/mail/send",
        headers={
            "Authorization": f"Bearer {SENDGRID_API_KEY}",
            "Content-Type": "application/json"
        },
        json=email_data
    )

    if response.status_code != 202:
        raise Exception(f"Failed to send email: {response.status_code} - {response.text}")
