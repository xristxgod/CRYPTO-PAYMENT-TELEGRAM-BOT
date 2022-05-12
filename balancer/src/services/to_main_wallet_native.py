import decimal
from typing import Optional

from src.__init__ import DB, ExSend
from src.services.get_balance import get_balance
from src.services.get_optomal_gas import get_optimal_gas
from src.services.send_transaction import create_transaction, sign_send_transaction
from config import Config, decimals, logger

async def is_native_dust(value: decimal.Decimal, gas: decimal.Decimal, limit: Optional[decimal.Decimal] = None) -> bool:
    if limit is not None:
        diff = value - limit
    else:
        diff = value - gas * Config.DUST_MULTIPLICATOR
    return diff < decimals.create_decimal('0.00000000')

async def send_to_main_wallet_native(address: str, limit: Optional[decimal.Decimal] = None):
    try:
        balance = await get_balance(address)
        gas_native = await get_optimal_gas(address, Config.BSC_ADMIN_ADDRESS, balance)
        if await is_native_dust(balance - gas_native, gas_native, limit=limit):
            return
        created_tx = await create_transaction(
            from_address=address,
            to_address=Config.BSC_ADMIN_ADDRESS,
            amount=balance - gas_native - decimals.create_decimal('0.00000001')
        )
        private_key = await DB.get_private_key(address)
        if private_key is not None:
            signed = await sign_send_transaction(
                payload=created_tx['createTxHex'],
                private_key=private_key
            )
            await ExSend.send_msg_to_kibana(msg=f'SENDED TO MAIN WALLET (BSC) {signed}')
    except Exception as error:
        logger.error(f'ERROR BALANCER: {error}')