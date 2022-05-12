from datetime import datetime

from src.__init__ import DB

class Utils:

    @staticmethod
    def convert_time(t: int) -> str:
        return datetime.fromtimestamp(int(t)).strftime('%d-%m-%Y %H:%M:%S')

    @staticmethod
    async def get_transaction_in_db(transaction_hash: str, transaction: dict) -> dict:
        transaction_in_db = await DB.get_transaction_by_hash(transaction_hash=transaction_hash)
        if transaction_in_db is None:
            return transaction
        transaction["sender"] = transaction_in_db[-4]
        transaction["recipient"] = transaction_in_db[-3]
        return transaction