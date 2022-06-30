import json
import warnings

import requests
from brownie import Contract, accounts, chain, config

warnings.filterwarnings("ignore")

TARGET = {
    "agent": "0xD44D8a8c125D4EFD0517c05fe6C87957a0E37301",
    "voting": "0xa6AaF7Ea9ed211068Edfe89C6eCADA0baeF7Bcf6",
    "token": "0x3b400213A480F9989Bb659F834d31De001f10670",
    "quorum": 15,
}

# address to create the vote from - you will need to modify this prior to mainnet use
accounts.add(config['wallets']['from_keys'])
SENDER = accounts[0]
#create_guild_account = '0x9C7c50496386E75aAa435384c26A7FAd78B2b290'
create_guild_account = '0xdA62500768bFBedBb5F81d1eec279385eEe9d51A'

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
    ("guild_controller", "0x9bc8994cD9512C5d7BE4dC15c3c9B31E06F9daA3", "create_guild", create_guild_account, guildType, guildRate)
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
    evm_script = prepare_evm_script()
    print("vote numbers: %s" % aragon.votesLength())
    print(evm_script)
    # evm_script = '0x0000000140907540d8a6C65c637785e8f8B742ae6b0b996800000104b61d27f60000000000000000000000002f50d538606fa9edd2b11e2446beb18c9d5846bb00000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000060000000000000000000000000000000000000000000000000000000000000006418dfe92100000000000000000000000069fb7c45726cfe2badee8317005d3f94be8388400000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000'
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
