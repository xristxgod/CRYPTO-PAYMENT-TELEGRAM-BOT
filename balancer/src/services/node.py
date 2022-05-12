from web3 import Web3, AsyncHTTPProvider, HTTPProvider
from web3.eth import AsyncEth
from web3.middleware import geth_poa_middleware

from src.urils.types import ERC20_ABI
from config import Config

class NodeBSC:
    abi = ERC20_ABI
    NODE_URL = Config.BSC_NODE_URL
    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super(NodeBSC, cls).__new__(cls)
        return cls.instance

    def __init__(self):
        self.async_node = Web3(AsyncHTTPProvider(self.NODE_URL), modules={'eth': (AsyncEth,)}, middlewares=[])
        self.node = Web3(HTTPProvider(self.NODE_URL),)
        self.node.middleware_onion.inject(geth_poa_middleware, layer=0)

    async def is_connect(self):
        """Find out the stability of the connection"""
        return {"status": self.node.isConnected()}

    @property
    def gas_price(self):
        """Get gas price"""
        return self.async_node.eth.gas_price

node_singleton = NodeBSC()