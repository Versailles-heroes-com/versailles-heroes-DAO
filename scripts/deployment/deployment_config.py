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
    {  # Core team vesting total: 242,400,000, count: 3
        "duration": 30 * YEAR,
        "can_disable": False,
        "admin": "0x06fbdf636a1aa32afce615221a3408134f0379c5",
        "recipients": {
            "0xA8A038003E27C94A92594630A7e53E7Ea0823c34": 60600000_000000000000000000,
            "0x006C1F692Aed31ebF8425e2A9c37BfFA2f084627": 60600000_000000000000000000,
            "0x006C1F692Aed31ebF8425e2A9c37BfFA2f084626": 60600000_000000000000000000,
            "0x006C1F692Aed31ebF8425e2A9c37BfFA2f084625": 60600000_000000000000000000,
        },
    },
    {  # Investors total: 169,680,000, count: 5
        "duration": 35 * YEAR,
        "can_disable": False,
        "admin": "0x06fbdf636a1aa32afce615221a3408134f0379c5",
        "recipients": {
            "0xB1D433C1B849ECaEB4C4aA3F79D111C372674Bc0": 33936000_000000000000000000,
            "0xdA62500768bFBedBb5F81d1eec279385eEe9d51A": 33936000_000000000000000000,
            "0xdA62500768bFBedBb5F81d1eec279385eEe9d51B": 33936000_000000000000000000,
            "0xdA62500768bFBedBb5F81d1eec279385eEe9d51C": 33936000_000000000000000000,
            "0xdA62500768bFBedBb5F81d1eec279385eEe9d51D": 33936000_000000000000000000,
        },
    },
    {  # Foundation total: 169,680,000, count: 5
        "duration": 35 * YEAR,
        "can_disable": False,
        "admin": "0x06fbdf636a1aa32afce615221a3408134f0379c5",  # versailles
        "recipients": {
            "0xB1D433C1B849ECaEB4C4aA3F79D111C372674Bc0": 33936000_000000000000000000,
            "0xDc0E6ca3dD99b14f05Ed3a5d737c74f5282c63A3": 33936000_000000000000000000,
            "0xDc0E6ca3dD99b14f05Ed3a5d737c74f5282c63A4": 33936000_000000000000000000,
            "0xDc0E6ca3dD99b14f05Ed3a5d737c74f5282c63A5": 33936000_000000000000000000,
            "0xDc0E6ca3dD99b14f05Ed3a5d737c74f5282c63A6": 33936000_000000000000000000,
        },
    },
]


def get_live_admin():
    # Admin and funding admin account objects used for in a live environment
    # May be created via accounts.load(name) or accounts.add(privkey)
    # https://eth-brownie.readthedocs.io/en/stable/account-management.html
    admin = '0x7155fa7cFB7D965d74d10250B59B1eE1a4b0eDd1'  #
    funding_admins = ['', '', '', '']
    return admin, funding_admins


if not rpc.is_active():
    # logic that only executes in a live environment
    web3.eth.setGasPriceStrategy(gas_strategy)
    web3.middleware_onion.add(middleware.time_based_cache_middleware)
    web3.middleware_onion.add(middleware.latest_block_based_cache_middleware)
    web3.middleware_onion.add(middleware.simple_cache_middleware)