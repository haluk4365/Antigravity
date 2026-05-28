import asyncio
import os
from dotenv import load_dotenv
from services.kie_api import KieAIService

load_dotenv()
kie = KieAIService(os.environ.get('KIE_API_KEY'))

async def main():
    balance_data = await asyncio.to_thread(kie.get_credit_balance)
    if balance_data and isinstance(balance_data, dict):
        data_block = balance_data.get("data", balance_data)
        if isinstance(data_block, dict):
            balance = float(data_block.get("balance", data_block.get("credit", 0)))
        else:
            balance = float(data_block)
        print(f"Kredi: {balance}")
    else:
        print(f"Sorgu sonucu: {balance_data}")

asyncio.run(main())
