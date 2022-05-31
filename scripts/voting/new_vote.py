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
    "agent": "0xA2D7fFaf8cd6C67e41E5372Be54260fe6591B3Ee",
    "voting": "0xd4Da2E403bb4E155B46bd26508b8F51014F1dD09",
    "token": "0xC858DB925e96B1dc4Fb3Af2e9AD215d16D9C4057",
    "quorum": 30,
}

VRH_DAO_CREATE_GUILD = {
    "agent": "0x9FAB5EfE2CAcc37a9a6da212987936B741428dAA",
    "voting": "0x30A3c983bA81b8481ec48978babb78948Bb5e4f0",
    "token": "0xC858DB925e96B1dc4Fb3Af2e9AD215d16D9C4057",
    "quorum": 15,
}

EMERGENCY_DAO = {
    "forwarder": "0xE5E94f76Cb6c7F250780319a786eCf94D8ccF2E6",
    "agent": "0x72f50a9016878e4ce837d5314355647484dc2d83",
    "voting": "0xb18811c42adb9fe8048c4912d137640ab3c79131",
    "token": "0xe8dbd31b8ce6e69c6d78cfba67678faf21e09550",
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
    #("voting_escrow", "0xF4B87E521759c93877dec0b31b17fE9f1805782E", "name")
    #("voting_escrow", "0xF4B87E521759c93877dec0b31b17fE9f1805782E", "commit_transfer_ownership", "0x7155fa7cFB7D965d74d10250B59B1eE1a4b0eDd1")
    #("guild_controller", "0x360f9C1FDAee0273a60F057f208BcBe253F0244f", "commit_transfer_create_guild_ownership", '0x9FAB5EfE2CAcc37a9a6da212987936B741428dAA')
    ("guild_controller", "0x360f9C1FDAee0273a60F057f208BcBe253F0244f", "apply_transfer_create_guild_ownership")
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
