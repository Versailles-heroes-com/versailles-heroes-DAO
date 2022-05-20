import warnings

from brownie import Contract
from hexbytes import HexBytes

warnings.filterwarnings("ignore")

# the vote ID you wish to decrypt
VOTE_ID = 0

# address of the contract where the vote was created
# ownership votes: 0x1A0B896824fB45983c9bC6183795D9c89682F446
# parameter votes: 0xbcff8b0b9419b9a88c44546519b1e909cf330399
#VOTING_ADDRESS = "0x1A0B896824fB45983c9bC6183795D9c89682F446"
VOTING_ADDRESS = "0xC2D3e2817023558100bbf714e82487aBe0C00e09"


def main(vote_id=VOTE_ID):
    print("decode vote:")
    print("vote address:", VOTING_ADDRESS)
    print("vote id:", vote_id)
    proxy = Contract.from_explorer(VOTING_ADDRESS)
    if hasattr(proxy, 'implementation'):
        aragon = Contract.from_explorer(VOTING_ADDRESS, as_proxy_for=proxy.implementation())
    else:
        aragon = proxy

    evm_script = aragon.getVote(vote_id)
    print("evm_script:")
    print("open: %s, executed: %s, startDate: %s, snapshotBlock: %s" % (evm_script['open'], evm_script['executed'], evm_script['startDate'], evm_script['snapshotBlock']))
    print("supportRequired: %s, minAcceptQuorum: %s" % (evm_script['supportRequired'], evm_script['minAcceptQuorum']))
    print("yea: %s, nay: %s, votingPower: %s" % (evm_script['yea'], evm_script['nay'], evm_script['votingPower']))
    print("script: ", evm_script['script'])
    print()
    script = HexBytes(evm_script['script'])

    idx = 4
    while idx < len(script):
        #target = Contract.from_explorer(script[idx : idx + 20])
        #if hasattr(target, 'implementation'):
        #    target = Contract.from_explorer(script[idx : idx + 20], as_proxy_for=target.implementation())
        target = Contract(script[idx : idx + 20])
        idx += 20
        length = int(script[idx : idx + 4].hex(), 16)
        idx += 4
        calldata = script[idx : idx + length]
        idx += length
        fn, inputs = target.decode_input(calldata)
        if calldata[:4].hex() == "0xb61d27f6":
            agent_target = Contract(inputs[0])
            fn, inputs = agent_target.decode_input(inputs[2])
            print(
                f"Call via agent ({target}):\n ├─ To: {agent_target}\n"
                f" ├─ Function: {fn}\n └─ Inputs: {inputs}\n"
            )
        else:
            print(f"Direct call:\n ├─ To: {target}\n ├─ Function: {fn}\n └─ Inputs: {inputs}")