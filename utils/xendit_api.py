
import httpx
import os
import base64

BASE_URL = "https://api.xendit.co"
XENDIT_SECRET_KEY = os.getenv("XENDIT_SECRET_KEY")

def get_auth_header():
    if not XENDIT_SECRET_KEY:
        raise Exception("XENDIT_SECRET_KEY environment variable not set.")
    # Xendit requires Basic Auth with base64 encoded secret key
    encoded = base64.b64encode(f"{XENDIT_SECRET_KEY}:".encode()).decode()
    return {"Authorization": f"Basic {encoded}", "Content-Type": "application/json"}

async def create_invoice(amount, user_id):
    headers = get_auth_header()
    data = {
        "external_id": f"telegram_{user_id}_{amount}",
        "amount": amount,
        "description": f"Top up for Telegram user {user_id}"
    }
    async with httpx.AsyncClient() as client:
        response = await client.post(f"{BASE_URL}/v2/invoices", json=data, headers=headers)
        if response.status_code == 201:
            return response.json()
        else:
            return {"error": response.text, "status_code": response.status_code}

async def create_withdrawal(amount, user_id, bank_code, account_number, account_holder_name):
    headers = get_auth_header()
    data = {
        "external_id": f"withdraw_{user_id}_{amount}",
        "amount": amount,
        "bank_code": bank_code,
        "account_holder_name": account_holder_name,
        "account_number": account_number,
        "description": f"Withdrawal for Telegram user {user_id}"
    }
    async with httpx.AsyncClient() as client:
        response = await client.post(f"{BASE_URL}/disbursements", json=data, headers=headers)
        if response.status_code == 201:
            return response.json()
        else:
            return {"error": response.text, "status_code": response.status_code}