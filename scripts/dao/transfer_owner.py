import json

from brownie import ERC20VRH, GuildController, VotingEscrow

from . import deployment_config as config
confs = 1

# guild_controller transfer create_guild_agent
guild_controller.commit_transfer_create_guild_ownership(CREATE_GUILD_AGENT_ADDRESS, {"from": owner})
guild_controller.apply_transfer_create_guild_ownership({"from": owner})

# guild_controller transfer ownership_agent
guild_controller.commit_transfer_ownership(OWNERSHIP_AGENT_ADDRESS, {"from": owner})
guild_controller.apply_transfer_ownership({"from": owner})

# voting_escrow transfer ownership_agent
voting_escrow.commit_transfer_ownership(OWNERSHIP_AGENT_ADDRESS, {"from": owner, "required_confs": confs})
voting_escrow.apply_transfer_ownership({"from": admin, "required_confs": confs})

# gas_escrow transfer ownership_agent
moh_gas_escrow.commit_transfer_ownership(OWNERSHIP_AGENT_ADDRESS, {"from": owner, "required_confs": confs})
moh_gas_escrow.apply_transfer_ownership({"from": owner, "required_confs": confs})

#erc20vrh.set_admin(new_admin, {"from": admin, "required_confs": confs})
#vesting.set_admin(new_admin, {"from": admin, "required_confs": confs})

vesting_escrow01.commit_transfer_ownership(OWNERSHIP_AGENT_ADDRESS, {"from": owner})
vesting_escrow01.apply_transfer_ownership(OWNERSHIP_AGENT_ADDRESS, {"from": owner})
vesting_escrow02.commit_transfer_ownership(OWNERSHIP_AGENT_ADDRESS, {"from": owner})
vesting_escrow02.apply_transfer_ownership(OWNERSHIP_AGENT_ADDRESS, {"from": owner})
vesting_escrow03.commit_transfer_ownership(OWNERSHIP_AGENT_ADDRESS, {"from": owner})
vesting_escrow03.apply_transfer_ownership(OWNERSHIP_AGENT_ADDRESS, {"from": owner})
