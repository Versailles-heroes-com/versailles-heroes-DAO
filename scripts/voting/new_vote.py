import json
import warnings

import requests
from brownie import Contract, accounts, chain, config

warnings.filterwarnings("ignore")

# this script is used to prepare, simulate and broadcast votes within Versailles's DAO
# modify the constants below according the the comments, and then use `simulate` in
# a forked mainnet to verify the result of the vote prior to broadcasting on mainnet

# addresses related to the DAO - these should not need modification
# as_proxy_for=0xa4D1a2693589840BABb7f3A44D14Fdf41b3bF1Fe (voting)
# as_proxy_for=0xa4D1a2693589840BABb7f3A44D14Fdf41b3bF1Fe (agent)
VRH_DAO_OWNERSHIP = {
    "agent": "0x1ea32Fc77717FD5A1670aaa4D32d8C985De4dD1B",
    "voting": "0x589f85f56c3Fab07341402acc4A2B811F4F26ab3",
    "token": "0x9e33f34870A0b55C7A4219da9989f382136772f1",
    "quorum": 30,
}

VRH_DAO_CREATE_GUILD = {
    "agent": "0xdCfC0B64F3E948f0560ED3Ded93E56E82eA473dF",
    "voting": "0xF6485c8c6C27a436d0dD1a482E062215fd804c73",
    "token": "0x9e33f34870A0b55C7A4219da9989f382136772f1",
    "quorum": 15,
}

EMERGENCY_DAO = {
    "forwarder": "0xE5E94f76Cb6c7F250780319a786eCf94D8ccF2E6",
    "agent": "0x72f50a9016878e4ce837d5314355647484dc2d83",
    "voting": "0xb18811c42adb9fe8048c4912d137640ab3c79131",
    "token": "0x9e33f34870A0b55C7A4219da9989f382136772f1",
    "quorum": 51,
}

# the intended target of the vote, should be one of the above constant dicts
TARGET = VRH_DAO_OWNERSHIP

# address to create the vote from - you will need to modify this prior to mainnet use
accounts.add(config['wallets']['from_keys'])
#SENDER = accounts.at("0x7155fa7cFB7D965d74d10250B59B1eE1a4b0eDd1", force=True)
SENDER = accounts[0]

# a list of calls to perform in the vote, formatted as a lsit of tuples
# in the format (target, function name, *input args).
#
# for example, to call:
# GaugeController("0x2F50D538606Fa9EDD2B11E2446BEb18C9D5846bB").add_gauge("0xFA712...", 0, 0)
#
# use the following:
# [("0x2F50D538606Fa9EDD2B11E2446BEb18C9D5846bB", "add_gauge", "0xFA712...", 0, 0),]
#
# commonly used addresses:
# GuildController - 0x2F50D538606Fa9EDD2B11E2446BEb18C9D5846bB
# Guild - 0x519AFB566c05E00cfB9af73496D00217A630e4D5
# GasEscrow - 0xeCb456EA5365865EbAb8a2661B0c503410e9B347

guildType = 0
guildRate = 20
ACTIONS = [
    # ("target", "fn_name", *args),
    #("voting_escrow", "0x27ee9a798b388448542a7165B75010231210D44A", "name")
    #("voting_escrow", "0x27ee9a798b388448542a7165B75010231210D44A", "commit_transfer_ownership", "0x7155fa7cFB7D965d74d10250B59B1eE1a4b0eDd1")
    #("guild_controller", "0xF5Fec47D9b81596BeDB5f505C9434a899DDD9D0E", "commit_transfer_create_guild_ownership", '0x9FAB5EfE2CAcc37a9a6da212987936B741428dAA')
    #("guild_controller", "0xF5Fec47D9b81596BeDB5f505C9434a899DDD9D0E", "apply_transfer_create_guild_ownership")
    #("guild_controller", "0xF5Fec47D9b81596BeDB5f505C9434a899DDD9D0E", "add_type", "Gas OOH", "OOH", "0x352447f66bDAf66c7c6748E2C07051C5f4c93ecF", 1 * 10 ** 18)
    #("guild_controller", "0xF5Fec47D9b81596BeDB5f505C9434a899DDD9D0E", "add_type", "GasOOH", "OOH", "0x352447f66bDAf66c7c6748E2C07051C5f4c93ecF", 1 * 10 ** 18)
    #("guild_controller", "0xF5Fec47D9b81596BeDB5f505C9434a899DDD9D0E", "change_type_weight", 0, 30)
    #("guild_controller", "0xF5Fec47D9b81596BeDB5f505C9434a899DDD9D0E", "change_guild_weight", "0xAC6AFe8f4f43a1B3957cC666E498FDc301942090", 40)
    #("guild_controller", "0xF5Fec47D9b81596BeDB5f505C9434a899DDD9D0E", "toggle_pause", "0xAC6AFe8f4f43a1B3957cC666E498FDc301942090")
    #("guild_controller", "0xF5Fec47D9b81596BeDB5f505C9434a899DDD9D0E", "change_guild_contract", "0x0000Fe8f4f43a1B3957cC666E498FDc301942090")
    #("guild_controller", "0xF5Fec47D9b81596BeDB5f505C9434a899DDD9D0E", "commit_transfer_ownership", "0xFFFFFFFFFFFFa1B3957cC666E498FDc301942090")
    #("guild_controller", "0xF5Fec47D9b81596BeDB5f505C9434a899DDD9D0E", "apply_transfer_ownership")
    #("vesting_escrow", "0xB57ebD560a526936A01C35380cc39769Bf626046", "commit_transfer_ownership", "0x7155fa7cFB7D965d74d10250B59B1eE1a4b0eDd1")
    #("vesting_escrow", "0xB57ebD560a526936A01C35380cc39769Bf626046", "apply_transfer_ownership")
    #("moh_token", "0x207E065f32EE9a1F95214A0ad59933E4EA02dc36", "mint", "0x006C1F692Aed31ebF8425e2A9c37BfFA2f084627", 1000000000000000000000000)
    ("moh_token", "0x207E065f32EE9a1F95214A0ad59933E4EA02dc36", "transferOwnership", "0x006C1F692Aed31ebF8425e2A9c37BfFA2f084627")
]

# description of the vote, will be pinned to IPFS
DESCRIPTION = "A description of the vote."

def get_abi(name):
    with open("abi/%s.abi" % name, "r") as f:
        aragon_abi = json.loads(f.read())
    return aragon_abi

def prepare_evm_script():
    # agent = Contract.from_explorer(TARGET["agent"])
    aragon_abi = get_abi("aragon-agent")
    agent = Contract.from_abi("agent", TARGET["agent"], aragon_abi)
    evm_script = "0x00000001"

    for name, address, fn_name, *args in ACTIONS:
        abi_info = get_abi(name)
        contract = Contract.from_abi(name, address, abi_info)
        fn = getattr(contract, fn_name)
        calldata = fn.encode_input(*args)
        agent_calldata = agent.execute.encode_input(address, 0, calldata)[2:]
        length = hex(len(agent_calldata) // 2)[2:].zfill(8)
        evm_script = f"{evm_script}{agent.address[2:]}{length}{agent_calldata}"

    return evm_script


def make_vote(sender=SENDER):
    text = json.dumps({"text": DESCRIPTION})
    # response = requests.post("https://ipfs.infura.io:5001/api/v0/add", files={"file": text}, auth=(infura_id, infura_secret))
    # ipfs_hash = response.json()["Hash"]  # QmRS6nMcnwQcYuP3JExDdrqsx3rrQxVFayVD8sHn2vGoV9
    ipfs_hash = "QmRS6nMcnwQcYuP3JExDdrqsx3rrQxVFayVD8sHn2vGoV9"
    print(f"ipfs hash: {ipfs_hash}")

    # aragon = Contract.from_explorer(TARGET["agent"], as_proxy_for=TARGET["voting"])
    proxy = Contract.from_explorer(TARGET["voting"])
    if hasattr(proxy, 'implementation'):
        aragon = Contract.from_explorer(TARGET["voting"], as_proxy_for=proxy.implementation())
    else:
        aragon = proxy
    #aragon = Contract(TARGET["voting"])
    evm_script = prepare_evm_script()
    print("vote numbers: %s", aragon.votesLength())
    if TARGET.get("forwarder"):
        # the emergency DAO only allows new votes via a forwarder contract
        # so we have to wrap the call in another layer of evm script
        vote_calldata = aragon.newVote.encode_input(evm_script, DESCRIPTION, False, False)[2:]
        length = hex(len(vote_calldata) // 2)[2:].zfill(8)
        evm_script = f"0x00000001{aragon.address[2:]}{length}{vote_calldata}"
        print(f"Target: {TARGET['forwarder']}\nEVM script: {evm_script}")
        tx = Contract(TARGET["forwarder"]).forward(evm_script, {"from": sender})
    else:
        print(f"Target: {aragon.address}\nEVM script: {evm_script}")
        tx = aragon.newVote(
            evm_script,
            f"ipfs:{ipfs_hash}",
            False,
            False,
            {"from": sender, "priority_fee": "2 gwei"},
        )

    vote_id = tx.events["StartVote"]["voteId"]

    print(f"\nSuccess! Vote ID: {vote_id}")
    return vote_id


def simulate():
    # make the new vote
    convex = "0x989aeb4d175e16225e39e87d0d97a3360524ad80"
    vote_id = make_vote(convex)

    # vote
    proxy = Contract.from_explorer(TARGET["voting"])
    if hasattr(proxy, 'implementation'):
        aragon = Contract.from_explorer(TARGET["voting"], as_proxy_for=proxy.implementation())
    else:
        aragon = proxy
    aragon.vote(vote_id, True, False, {"from": convex})

    # sleep for a week so it has time to pass
    chain.sleep(86400 * 7)

    # moment of truth - execute the vote!
    aragon.executeVote(vote_id, {"from": accounts[0]})


def main():
    print("accounts: ", SENDER.address, SENDER.balance(), SENDER.private_key)
    vote_id = make_vote(sender=SENDER)
    print("please vote id: %s" % vote_id)
