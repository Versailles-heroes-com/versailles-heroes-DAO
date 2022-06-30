"""
Deployment Configuration file
=============================
This script holds customizeable / sensetive values related to the DAO deployment scripts.
See `README.md` in this directory for more information on how deployment works.
"""

from brownie import rpc, web3
from web3 import middleware
from web3.gas_strategies.time_based import fast_gas_price_strategy as gas_strategy

VESTING_JSON = "scripts/early-users.json"
DEPLOYMENTS_JSON = "deployments.json"
REQUIRED_CONFIRMATIONS = 3

# Aragon agent address - set after the Aragon DAO is deployed
ARAGON_AGENT = None

YEAR = 86400 * 365

# `VestingEscrow` contracts to be deployed
STANDARD_ESCROWS = [
    {  # Core team vesting total: 242,400,000, count: 4
        "duration": 30 * YEAR,
        "can_disable": False,
        "admin": "0x000000000000000000000000000000000000000A",
        "recipients": {
            "0x0000000000000000000000000000000000000001": 60600000_000000000000000000,
            "0x0000000000000000000000000000000000000002": 60600000_000000000000000000,
            "0x0000000000000000000000000000000000000003": 60600000_000000000000000000,
            "0x0000000000000000000000000000000000000004": 60600000_000000000000000000,
        },
    },
    {  # Investors total: 169,680,000, count: 5
        "duration": 35 * YEAR,
        "can_disable": False,
        "admin": "0x000000000000000000000000000000000000000B",
        "recipients": {
            "0x0000000000000000000000000000000000000001": 33936000_000000000000000000,
            "0x0000000000000000000000000000000000000002": 33936000_000000000000000000,
            "0x0000000000000000000000000000000000000003": 33936000_000000000000000000,
            "0x0000000000000000000000000000000000000004": 33936000_000000000000000000,
            "0x0000000000000000000000000000000000000005": 33936000_000000000000000000,
        },
    },
    {  # Foundation total: 169,680,000, count: 8
        "duration": 35 * YEAR,
        "can_disable": False,
        "admin": "0x000000000000000000000000000000000000000C",  # versailles
        "recipients": {
            "0x0000000000000000000000000000000000000001": 21210000_000000000000000000,
            "0x0000000000000000000000000000000000000002": 21210000_000000000000000000,
            "0x0000000000000000000000000000000000000003": 21210000_000000000000000000,
            "0x0000000000000000000000000000000000000004": 21210000_000000000000000000,
            "0x0000000000000000000000000000000000000005": 21210000_000000000000000000,
            "0x0000000000000000000000000000000000000006": 21210000_000000000000000000,
            "0x0000000000000000000000000000000000000007": 21210000_000000000000000000,
            "0x0000000000000000000000000000000000000008": 21210000_000000000000000000,
        },
    },
]


def get_live_admin():
    # Admin and funding admin account objects used for in a live environment
    # May be created via accounts.load(name) or accounts.add(privkey)
    # https://eth-brownie.readthedocs.io/en/stable/account-management.html
    admin = '0x0000000000000000000000000000000000000AAA'  #
    funding_admins = ['', '', '', '']
    return admin, funding_admins


if not rpc.is_active():
    # logic that only executes in a live environment
    web3.eth.setGasPriceStrategy(gas_strategy)
    web3.middleware_onion.add(middleware.time_based_cache_middleware)
    web3.middleware_onion.add(middleware.latest_block_based_cache_middleware)
    web3.middleware_onion.add(middleware.simple_cache_middleware)