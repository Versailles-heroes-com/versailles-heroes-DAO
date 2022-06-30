import json

from brownie import ERC20VRH, VestingEscrow, config, accounts

from . import deployment_config

ZERO_ADDRESS = "0x0000000000000000000000000000000000000000"
YEAR = 86400 * 365


def live():
    """
    Vest tokens in a live environment.
    """
    accounts.add(config['wallets']['from_keys'])
    print("accounts: ", accounts)
    admin, _ = deployment_config.get_live_admin()

    with open(deployment_config.DEPLOYMENTS_JSON) as fp:
        deployments = json.load(fp)

    vest_tokens(admin, deployments["ERC20VRH"], deployment_config.REQUIRED_CONFIRMATIONS)


def development():
    """
    Vest tokens in a development environment and validate the result.
    """
    token = ERC20VRH.deploy("Versailles Heroes Token", "VRH", 18, {"from": accounts[0]})
    vesting_escrow, vested_amounts = vest_tokens(accounts[0], token, 1)
    sanity_check(token, vesting_escrow, vested_amounts)


def vest_tokens(admin, token_address, confs):
    admin = accounts.at(admin)
    print("admin: ", admin)
    token = ERC20VRH.at(token_address)

    # deploy standard escrows
    start_time = token.future_epoch_time_write.call()
    for data in deployment_config.STANDARD_ESCROWS:

        vesting_escrow = VestingEscrow.deploy(
            token,
            start_time,
            start_time + data["duration"],
            data["can_disable"],
            [ZERO_ADDRESS] * 4,
            {"from": admin, "required_confs": confs},
        )
        data["contract"] = vesting_escrow

        total_amount = sum(data["recipients"].values())
        token.approve(vesting_escrow, total_amount, {"from": admin, "required_confs": confs})
        vesting_escrow.add_tokens(total_amount, {"from": admin, "required_confs": confs})

        zeros = 100 - len(data["recipients"])
        fund_inputs = tuple(data["recipients"].items())
        recipients = [i[0] for i in fund_inputs] + [ZERO_ADDRESS] * zeros
        amounts = [i[1] for i in fund_inputs] + [0] * zeros

        vesting_escrow.fund(recipients, amounts, {"from": admin, "required_confs": confs})

        if "admin" in data:
            vesting_escrow.commit_transfer_ownership(
                data["admin"], {"from": admin, "required_confs": confs}
            )
            vesting_escrow.apply_transfer_ownership({"from": admin, "required_confs": confs})

    print("\nStandard Escrows:")
    for data in deployment_config.STANDARD_ESCROWS:
        total_amount = sum(data["recipients"].values())
        print(
            f"  {data['contract'].address}: {len(data['recipients'])} recipients, "
            f"{total_amount} total tokens, {data['duration']/YEAR} year lock"
        )

    return deployment_config.STANDARD_ESCROWS


def sanity_check(token, standard_escrows):

    for data in standard_escrows:
        escrow = data["contract"]
        total_amount = sum(data["recipients"].values())
        if escrow.initial_locked_supply() != total_amount:
            raise ValueError(
                f"Unexpected locked supply in {escrow.address}: {escrow.initial_locked_supply()}"
            )
        if escrow.unallocated_supply() != 0:
            raise ValueError(
                f"Unallocated supply remains in {escrow.address}: {escrow.unallocated_supply()}"
            )

        for recipient, expected in data["recipients"].items():
            balance = escrow.initial_locked(recipient)
            if balance != expected:
                raise ValueError(
                    f"Incorrect vested amount for {recipient} in {escrow.address} "
                    f"- expected {expected}, got {balance}"
                )

    print("Sanity check passed!")