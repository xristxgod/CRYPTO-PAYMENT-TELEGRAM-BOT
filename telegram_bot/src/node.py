from web3 import Web3, AsyncHTTPProvider, HTTPProvider
from web3.eth import AsyncEth
from web3.middleware import geth_poa_middleware
from ecdsa.curves import SECP256k1
from eth_utils import to_checksum_address, keccak as eth_utils_keccak

from src.types import ERC20_ABI
from config import Config

class PublicKey:
    BIP32_CURVE = SECP256k1

    def __init__(self, private_key: str):
        self.__point = int.from_bytes(private_key, byteorder='big') * self.BIP32_CURVE.generator

    def __bytes__(self):
        x_str = self.__point.x().to_bytes(32, byteorder='big')
        parity = self.__point.y() & 1
        return (2 + parity).to_bytes(1, byteorder='big') + x_str

    def address(self):
        x = self.__point.x()
        y = self.__point.t()
        s = x.to_bytes(32, 'big') + y.to_bytes(32, 'big')
        return to_checksum_address(eth_utils_keccak(s)[12:])

class NodeBSC:
    abi = ERC20_ABI

    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super(NodeBSC, cls).__new__(cls)
        return cls.instance

    def __init__(self):
        self.async_node = Web3(AsyncHTTPProvider(Config.BSC_NODE_URL), modules={"eth": (AsyncEth,)}, middlewares=[])
        self.node = Web3(HTTPProvider(Config.BSC_NODE_URL))
        self.node.middleware_onion.inject(geth_poa_middleware)

    async def is_connect(self):
        """Find out the stability of the connection"""
        return {"status": self.node.isConnected()}

    @property
    def gas_price(self):
        """Get gas price"""
        return self.async_node.eth.gas_price

node_singleton = NodeBSC()