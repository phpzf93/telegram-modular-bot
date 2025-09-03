import httpx

XENDIT_API_KEY = "xnd_public_production_D1sFUR53TtvTrsf7RdnGlw_I__JwpNd8kwtHkAp9CByR93pSdNz0kjJS1wmjATZf"
BASE_URL = "https://api.xendit.co"

async def create_invoice(amount, user_id):
    headers = {
        "Authorization": f"Basic {XENDIT_API_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "external_id": f"telegram_{user_id}_{amount}",
        "amount": amount,
        "description": f"Top up for Telegram user {user_id}"
    }
    async with httpx.AsyncClient() as client:
        response = await client.post(f"{BASE_URL}/v2/invoices", json=data, headers=headers)
        return response.json()

async def create_withdrawal(amount, user_id):
    # Placeholder: Xendit withdrawal API integration needed
    return {"status": "pending", "amount": amount, "user_id": user_id}