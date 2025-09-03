import httpx
import os
import base64

BASE_URL = "https://api.xendit.co"

def get_auth_header():
    secret_key = os.getenv("XENDIT_SECRET_KEY")
    if not secret_key:
        raise Exception("XENDIT_SECRET_KEY environment variable not set.")
    # Xendit requires Basic Auth with base64 encoded secret key
    encoded = base64.b64encode(f"{secret_key}:".encode()).decode()
    return {"Authorization": f"Basic {encoded}", "Content-Type": "application/json"}

async def create_invoice(amount, user_id):
    headers = get_auth_header()
    data = {
        "external_id": f"telegram_{user_id}_{amount}",
        "amount": amount,
        "description": f"Top up for Telegram user {user_id}"
    }
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(f"{BASE_URL}/v2/invoices", json=data, headers=headers)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            return {"error": str(e), "status_code": e.response.status_code, "details": e.response.text}
        except Exception as e:
            return {"error": str(e)}

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
        try:
            response = await client.post(f"{BASE_URL}/disbursements", json=data, headers=headers)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            return {"error": str(e), "status_code": e.response.status_code, "details": e.response.text}
        except Exception as e:
            return {"error": str(e)}