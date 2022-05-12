import binascii

from mnemonic import Mnemonic

from src.models import Wallet
from src.node import node_singleton, PublicKey

async def create_wallet(user_id):
    """Create a tron wallet"""
    words = Mnemonic("english").generate(strength=128)
    try:
        node_singleton.node.eth.account.enable_unaudited_hdwallet_features()
        __wallet = node_singleton.node.eth.account.from_mnemonic(mnemonic=words)
        return await Wallet.create(
            address=__wallet.address.lower(),
            private_key=node_singleton.async_node.toHex(__wallet.key),
            public_key=binascii.hexlify(bytes(PublicKey(__wallet.key))).decode("utf-8"),
            user_id=user_id
        )
    except:
        return None