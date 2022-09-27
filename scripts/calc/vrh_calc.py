import json, time

from brownie import (
    Contract,
    ERC20VRH,
    ERC20Gas,
    GasEscrow,
    Guild,
    GuildController,
    Minter,
    RewardVestingEscrow,
    VestingEscrow,
    VotingEscrow,
    chain
)

# accounts
zero_addr = '0x0000000000000000000000000000000000000000'
acc00 = '0x7155fa7cFB7D965d74d10250B59B1eE1a4b0eDd1'
acc01 = '0x9C7c50496386E75aAa435384c26A7FAd78B2b290'
acc02 = '0x006C1F692Aed31ebF8425e2A9c37BfFA2f084627'
acc04 = '0xDc0E6ca3dD99b14f05Ed3a5d737c74f5282c63A3'
acc15 = '0xDA2D4E7370F7A35b27A2d6f132765b29f33DA11a'
account_group = [acc00, acc01, acc02, acc04, acc15]

# contract address
guild_controller_address = "0xF5Fec47D9b81596BeDB5f505C9434a899DDD9D0E"

vesting_escrow01_address = "0x81DB4C2e2af3D3Cd9E956dC2C1c0F75EF23E4E57"
vesting_escrow02_address = "0xB57ebD560a526936A01C35380cc39769Bf626046"
vesting_escrow03_address = "0x4C48795631690587F4556Cc28B8C88C65A73dcea"

# load contract
guild_controller = GuildController.at(guild_controller_address)
vesting_escrow01 = VestingEscrow.at(vesting_escrow01_address)
vesting_escrow02 = VestingEscrow.at(vesting_escrow02_address)
vesting_escrow03 = VestingEscrow.at(vesting_escrow03_address)

vrh_token = ERC20VRH.at(guild_controller.token())
moh_gas_escrow = GasEscrow.at(guild_controller.gas_type_escrow(0))
moh_token = ERC20Gas.at(moh_gas_escrow.token())
voting_escrow = VotingEscrow.at(guild_controller.voting_escrow())
minter = Minter.at(guild_controller.minter())
reward_vesting = RewardVestingEscrow.at(minter.rewardVestingEscrow())

with open('abi/guild_view.abi', 'r') as f:
    guild_view_abi = json.loads(f.read())

curr_time = chain.time()
DAY = 86400
WEEK = DAY * 7
YEAR = DAY * 365
DECIMALS = 10 ** 18

guilds_list = []
for i in range(guild_controller.n_guilds()):
    guilds_list.append(Contract.from_abi("guild", guild_controller.guilds(i), guild_view_abi))

def home():
    print("Home pager.")
    erc20VrhRate = vrh_token.rate()
    erc20VrhTotalSupply = vrh_token.totalSupply()
    votingEscrowTotalSupply = voting_escrow.totalSupply()
    votingEscrowTotalSupply24Before = 0 #(voting_escrow.totalSupply() - voting_escrow.totalSupply(curr_time - DAY))
    votingEscrowSupply = voting_escrow.supply()
    vrhMintable24H = 0 #vrh_token.mintable_in_timeframe(curr_time - DAY, curr_time)
    vestingEscrowLockedSupply1 = vesting_escrow01.lockedSupply()
    vestingEscrowLockedSupply2 = vesting_escrow02.lockedSupply()
    vestingEscrowLockedSupply3 = vesting_escrow03.lockedSupply()
    vrhAverageApy = erc20VrhRate * YEAR / votingEscrowTotalSupply
    vrhAverageLockTime = 4 * votingEscrowTotalSupply / votingEscrowSupply
    votingEscrow24Increase = 0
    vrhCirculation = erc20VrhTotalSupply - votingEscrowSupply - vestingEscrowLockedSupply1 - vestingEscrowLockedSupply2 - vestingEscrowLockedSupply3

    print("erc20VrhRate:", erc20VrhRate / DECIMALS)
    print("erc20VrhTotalSupply:", erc20VrhTotalSupply / DECIMALS)
    print("votingEscrowTotalSupply:", votingEscrowTotalSupply / DECIMALS)
    print("votingEscrowTotalSupply24Before:", votingEscrowTotalSupply24Before / DECIMALS)
    print("votingEscrowSupply:", votingEscrowSupply / DECIMALS)
    print("votingEscrowSupply24Before:", 0)
    print("vrhMintable24H:", vrhMintable24H / DECIMALS)
    print("vestingEscrowLockedSupply1:", vestingEscrowLockedSupply1 / DECIMALS)
    print("vestingEscrowLockedSupply2:", vestingEscrowLockedSupply2 / DECIMALS)
    print("vestingEscrowLockedSupply3:", vestingEscrowLockedSupply3 / DECIMALS)
    print("vrhAverageApy:", vrhAverageApy)
    print("vrhAverageLockTime:", vrhAverageLockTime)
    print("votingEscrow24Increase:", votingEscrow24Increase / DECIMALS)
    print("vrhCirculation:", vrhCirculation / DECIMALS)
    print("+" * 40)

    # MOH burned, MOH Total
    erc20TotalSupply = moh_token.totalSupply()
    gasEscrowSupply = moh_gas_escrow.supply()
    gasEscrowTotalSupply = moh_gas_escrow.totalSupply()

    print("erc20TotalSupply:", erc20TotalSupply / DECIMALS)
    print("gasEscrowSupply:", gasEscrowSupply / DECIMALS)
    print("gasEscrowTotalSupply:", gasEscrowTotalSupply / DECIMALS)
    print("erc20TotalSupply24HChange:", 0)
    print("gasEscrowSupply24HChange:", 0)
    print("gasEscrowTotalSupply24HChange:", 0)
    print("+" * 40)

    # guild value
    for i in guilds_list:
        #guild = Guild.at(i)
        print("guildId:", guilds_list.index(i))
        guild = Contract.from_abi("guild:", i, guild_view_abi)
        gas_token_addr = GasEscrow.at(guild.gas_escrow())
        guildWeight = guild_controller.guild_effective_weight(guild)
        guild_relative_weight = guild_controller.guild_relative_weight(guild.address)
        guild_commission_rate = guild.commission_rate(guild.last_change_rate())
        guildWorkingSupply = guild.working_supply()
        apy_from = vrh_token.rate() * guild_controller.guild_relative_weight(guild) * YEAR * 0.4 / guildWorkingSupply / 100
        apy_to = vrh_token.rate() * guild_controller.guild_relative_weight(guild) * YEAR / guildWorkingSupply / 100
        print("address:", guild.address)
        print("gasEscrowAddress:", guild.gas_escrow())
        print("guildWeight:", guildWeight / DECIMALS)
        print("boosting symbol:", gas_token_addr.symbol())
        print("guild_relative_weight:", guild_relative_weight / DECIMALS)
        print("guild_effective_weight:", guild_controller.guild_effective_weight(guild) / DECIMALS)
        print("guild_commission_rate:", guild_commission_rate)
        print("guildWorkingSupply:", guildWorkingSupply / DECIMALS)
        print("apyFrom: %.2F" % apy_from)
        print("apyTo: %.2F" % apy_to)
        print("-" * 40)
    print("+" * 40)

def dashbord():
    print("Dashbord pager.")
    print("+" * 40)
    for acc_addr in account_group:
        print("accounts:", acc_addr)
        guild_addr = guild_controller.global_member_list(acc_addr)
        vrh_balance = vrh_token.balanceOf(acc_addr)
        vevrh_balance = voting_escrow.balanceOf(acc_addr)
        moh_balance = moh_token.balanceOf(acc_addr)
        vesting_locked_rewards = reward_vesting.balanceOf(acc_addr) - reward_vesting.get_claimable_tokens(acc_addr)
        claimed_rewards = 0
        total_rewards = 0
        guild_owner_bonus = 0
        vrh_lock_amount = voting_escrow.locked(acc_addr)['amount']
        vrh_lock_end = voting_escrow.locked__end(acc_addr)
        moh_burned_amount = moh_gas_escrow.burned(acc_addr)['amount']
        moh_burned_end = moh_gas_escrow.burned__end(acc_addr)
        if guild_addr != zero_addr:
            print("guild_addr", guild_addr)
            guild = Contract.from_abi("guild", guild_addr, guild_view_abi)
            claimableToken = guild.claimable_tokens(acc_addr)
            guild_owner = guild.owner()
            guild_owner_bonus = guild.total_owner_bonus(guild_owner)
            if guild_owner == acc_addr:
                print("acc is owner")
        else:
            claimableToken = reward_vesting.get_claimable_tokens(acc_addr)
        print("claimableToken:", claimableToken / DECIMALS)
        print("vrh_balance:", vrh_balance / DECIMALS)
        print("vevrh_balance:", vevrh_balance / DECIMALS)
        print("moh_balance:", moh_balance / DECIMALS)
        print("vesting_locked_rewards:", vesting_locked_rewards / DECIMALS)
        print("claimed_rewards:", claimed_rewards / DECIMALS)
        print("total_rewards:", total_rewards / DECIMALS)
        print("guild_owner_bonus:", guild_owner_bonus / DECIMALS)
        print("vrh_lock_amount:", vrh_lock_amount / DECIMALS)
        print("vrh_lock_end:", time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(vrh_lock_end)))
        print("moh_burned_amount:", moh_burned_amount / DECIMALS)
        print("moh_burned_end:", time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(moh_burned_end)))
        print("-" * 40)
    print("+" * 40)

def main():
    print("*" * 80)
    home()
    print("*" * 80)
    dashbord()
    print("*" * 80)
    print("all done.")
