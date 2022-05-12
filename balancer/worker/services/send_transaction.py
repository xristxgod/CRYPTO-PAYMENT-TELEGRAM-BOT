from src.services.to_main_wallet_native import send_to_main_wallet_native

async def send_transaction_service(address):
    await send_to_main_wallet_native(address)