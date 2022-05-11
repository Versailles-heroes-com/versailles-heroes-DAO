from audioop import mul
from brownie import chain
import brownie
import pytest

H = 3600
DAY = 86400
WEEK = 7 * DAY
MAXTIME = 126144000
TOL = 120 / WEEK

@pytest.fixture(scope="module", autouse=True)
def initial_setup(web3, chain, accounts, token, gas_token, voting_escrow, guild_controller, minter, vesting, multisig):
    alice, bob = accounts[:2]

    multisig.initialise([alice, bob], 1)

    amount_alice = 40000 * 10 ** 18
    amount_bob = 50000 * 10 ** 18
    token.transfer(alice, amount_alice, {"from": multisig.address})
    token.transfer(bob, amount_bob, {"from": multisig.address})
    stages = {}

    chain.sleep(DAY + 1)
    token.update_mining_parameters()

    token.approve(voting_escrow.address, amount_alice * 10, {"from": alice})
    token.approve(voting_escrow.address, amount_bob * 10, {"from": bob})

    assert voting_escrow.totalSupply() == 0
    assert voting_escrow.balanceOf(alice) == 0
    assert voting_escrow.balanceOf(bob) == 0

    # Move to timing which is good for testing - beginning of a UTC week
    chain.sleep((chain[-1].timestamp // WEEK + 1) * WEEK - chain[-1].timestamp)
    chain.mine()

    chain.sleep(H)

    stages["before_deposits"] = (web3.eth.blockNumber, chain[-1].timestamp)

    voting_escrow.create_lock(amount_alice, chain[-1].timestamp + MAXTIME, {"from": alice})
    voting_escrow.create_lock(amount_bob, chain[-1].timestamp + MAXTIME, {"from": bob})
    stages["alice_deposit"] = (web3.eth.blockNumber, chain[-1].timestamp)

    chain.sleep(H)
    chain.mine()

    token.set_minter(minter.address, {"from": multisig.address})
    guild_controller.set_minter(minter.address, {"from": multisig.address})
    vesting.set_minter(minter.address, {"from": multisig.address})
    chain.sleep(10)

def test_add_remove_signers(chain, accounts, guild_controller, multisig):
    alice, bob, john = accounts[:3]

    # check if alice and bob exist after setup and john to be false
    assert multisig.is_signer(alice) == True
    assert multisig.is_signer(bob) == True
    assert multisig.is_signer(john) == False

    # try adding bob again.
    with brownie.reverts('signer already exist'):
       multisig.add_signer(bob, {'from': alice})

    # will remove bob from signer list
    tx1 = multisig.remove_signer(bob, {'from': alice})

    assert tx1.events[0]['removed_signer'] == bob
    assert multisig.is_signer(bob) == False

    # add john in with bob, which will result in fail because bob is not a signer anymore
    with brownie.reverts('sender must be part of signers to add in new signer'):
       multisig.add_signer(john, {'from': bob})
    
    tx2 = multisig.add_signer(john, {'from': alice})

    assert tx2.events[0]['new_signer'] == john
    assert multisig.is_signer(john) == True

def test_submit_proposal(accounts, guild_controller, multisig):
    alice, bob, john = accounts[:3]

    multisig.set_number_of_approvals(2)

    # add in john
    tx1 = multisig.add_signer(john, {'from': alice})

    assert tx1.events[0]['new_signer'] == john
    assert multisig.is_signer(john) == True

    # submit proposal
    tx2 = multisig.submit_proposal(alice, guild_controller.address, 'toggle_pause', brownie.convert.to_bytes('',type_str='bytes32'), 'toggle_pause')

    assert tx2.events[0]['remarks'] == 'toggle_pause'
    assert tx2.events[0]['proposal_id'] == 0

    tx2 = multisig.submit_proposal(alice, guild_controller.address, 'toggle_pause', brownie.convert.to_bytes('',type_str='bytes32'), 'toggle_pause')

    assert tx2.events[0]['remarks'] == 'toggle_pause'
    assert tx2.events[0]['proposal_id'] == 1

    # try getting proposal details
    _result1 = multisig.get_proposal_with_proposal_id(guild_controller.address, 0, {'from': alice})
    assert _result1.return_value[1] == False

    # try getting proposal details
    _result2 = multisig.get_proposal_with_proposal_id(guild_controller.address, 1, {'from': alice})
    assert _result2.return_value[1] == False

def test_approve_proposal(accounts, guild_controller, multisig):
    alice, bob, john = accounts[:3]

    multisig.set_number_of_approvals(2)

    # add in john
    tx1 = multisig.add_signer(john, {'from': alice})

    assert tx1.events[0]['new_signer'] == john
    assert multisig.is_signer(john) == True

    # submit proposal
    tx2 = multisig.submit_proposal(alice, guild_controller.address, 'toggle_pause', brownie.convert.to_bytes('',type_str='bytes32'), 'toggle_pause')

    assert tx2.events[0]['remarks'] == 'toggle_pause'
    assert tx2.events[0]['proposal_id'] == 0
    
    # try getting proposal details
    _result1 = multisig.get_proposal_with_proposal_id(guild_controller.address, 0, {'from': alice})
    assert _result1.return_value[2] == 0

    multisig.approve_proposal(guild_controller.address, 0, {'from': alice})

    # access proposal to check if approval increased.
    _proposal = multisig.proposals(guild_controller.address,0)

    assert _proposal[2] == 1

def test_approve_then_execute(accounts, guild_controller, multisig):
    alice, bob, john = accounts[:3]

    multisig.set_number_of_approvals(2)

    # add in john
    tx1 = multisig.add_signer(john, {'from': alice})

    assert tx1.events[0]['new_signer'] == john
    assert multisig.is_signer(john) == True

    # submit proposal
    tx2 = multisig.submit_proposal(alice, guild_controller.address, 'toggle_pause', brownie.convert.to_bytes('',type_str='bytes32'), 'toggle_pause')

    assert tx2.events[0]['remarks'] == 'toggle_pause'
    assert tx2.events[0]['proposal_id'] == 0
    
    # try getting proposal details
    _result1 = multisig.get_proposal_with_proposal_id(guild_controller.address, 0, {'from': alice})
    assert _result1.return_value[2] == 0

    multisig.approve_proposal(guild_controller.address, 0, {'from': alice})

    # access proposal to check if approval increased.
    _proposal = multisig.proposals(guild_controller.address,0)

    assert _proposal[2] == 1

    # multisig.approve_proposal(guild_controller.address, 0, {'from': bob})

    # submit proposal
    tx3 = multisig.submit_proposal(alice, guild_controller.address, 'toggle_pause', brownie.convert.to_bytes('',type_str='bytes32'), 'toggle_pause')

    assert tx3.events[0]['remarks'] == 'toggle_pause'
    assert tx3.events[0]['proposal_id'] == 1

    multisig.approve_proposal(guild_controller.address, 1, {'from': alice})

    # try to approve same transaction twice
    with brownie.reverts('sender has already approve proposal'):
        multisig.approve_proposal(guild_controller.address, 1, {'from': alice})

def test_execute_proposal(accounts, guild_controller, multisig, gas_token, Guild):
    '''
    This test will try the following test:
    1. 1 approval execution
    2. 2 approval execution with 3 members
    '''
    alice, bob, john = accounts[:3]

     # create guild
    guild_obj = create_guild(chain, guild_controller, gas_token, alice, Guild, multisig)
    
     # submit proposal
    tx2 = multisig.submit_proposal(alice, guild_controller.address, 'toggle_pause', brownie.convert.to_bytes(guild_obj.address,type_str='bytes32'), 'toggle_pause')

    assert tx2.events[0]['remarks'] == 'toggle_pause'
    assert tx2.events[0]['proposal_id'] == 0

    # approve proposal
    tx3 = multisig.approve_proposal(guild_controller.address, 0, {'from': alice})

    assert tx3.events[1]['pause'] == True

    # approval should be executed and get proposal details
    _result1 = multisig.get_proposal_with_proposal_id(guild_controller.address, 0, {'from': alice})
    assert _result1.return_value[1] == True

    '''
    2. approval execution with 3 members 
    '''

    # increase number of approval
    multisig.set_number_of_approvals(2)

    # # create guild
    # guild_obj2 = create_guild(chain, guild_controller, gas_token, bob, Guild, multisig)
    

     # add in john
    tx1 = multisig.add_signer(john, {'from': alice})

    assert tx1.events[0]['new_signer'] == john
    assert multisig.is_signer(john) == True

    # submit new proposal
    tx2 = multisig.submit_proposal(alice, guild_controller.address, 'toggle_pause', brownie.convert.to_bytes(guild_obj.address,type_str='bytes32'), 'toggle_pause')

    assert tx2.events[0]['remarks'] == 'toggle_pause'
    assert tx2.events[0]['proposal_id'] == 1

    multisig.approve_proposal(guild_controller.address, 1, {'from': alice})
    tx4 = multisig.approve_proposal(guild_controller.address, 1, {'from': bob})

    assert tx4.events[1]['pause'] == False

    # approval should be executed and get proposal details
    _result1 = multisig.get_proposal_with_proposal_id(guild_controller.address, 0, {'from': alice})
    assert _result1.return_value[1] == True

def test_revoke_approval(accounts, guild_controller, multisig):
    alice, bob, john = accounts[:3]

     # increase number of approval
    multisig.set_number_of_approvals(2)

    tx2 = multisig.submit_proposal(alice, guild_controller.address, 'toggle_pause', brownie.convert.to_bytes('',type_str='bytes32'), 'toggle_pause')

    assert tx2.events[0]['remarks'] == 'toggle_pause'
    assert tx2.events[0]['proposal_id'] == 0

    multisig.approve_proposal(guild_controller.address, 0, {'from': alice})

    # access proposal to check if approval increased.
    _proposal = multisig.proposals(guild_controller.address,0)

    assert _proposal[2] == 1

    multisig.revoke_proposal_approval(guild_controller.address, 0, {'from': alice})

    # access proposal to check if approval decreased.
    _proposal = multisig.proposals(guild_controller.address,0)

    assert _proposal[2] == 0

def test_guildcontroller_toggle_pause(accounts, guild_controller, multisig, gas_token, Guild):
    alice, bob, john = accounts[:3]

    # create guild
    guild_obj = create_guild(chain, guild_controller, gas_token, alice, Guild, multisig)

     # increase number of approval
    multisig.set_number_of_approvals(2)

    # TODO: check on how to mitigate this vulnerability
    guild_controller.toggle_pause(guild_obj.address, {'from': multisig.address})

def create_guild(chain, guild_controller, gas_token, guild_owner, Guild, multisig):
    guild_type = 0
    guild_rate = 20
    type_weight = 1 * 10 ** 18
    guild_controller.add_type("Gas MOH", "GASMOH", gas_token.address, type_weight)
    chain.sleep(H)
    guild_controller.create_guild(guild_owner, guild_type, guild_rate, {"from": multisig.address})
    guild_address = guild_controller.guild_owner_list(guild_owner)
    guild_contract = Guild.at(guild_address)
    guild_contract.update_working_balance(guild_owner, {"from": guild_owner})
    return guild_contract





