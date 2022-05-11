# @version ^0.3.2

# interface
interface GuildController:
    def change_guild_contract(new_addr: address): payable
    def change_gas_escrow_contract(new_addr: address): payable
    def toggle_pause(addr: address): nonpayable

# struct
struct Proposal:
    proposal_id: uint256
    executed: bool
    approvals: uint256
    method_name_id: String[100]
    data: bytes32
    destination: address
    requestor: address
    approvers: DynArray[address, 100]
    remarks: String[100]

# signer
signers: public(DynArray[address, 100])

# signer => bool
is_signer: public(HashMap[address, bool])

# contract address => Proposals
proposals: public(HashMap[address, DynArray[Proposal, 1000]])

# guild => number of approvals
number_of_approvals: public(uint256)

# signer => Proposal index => bool
is_approved: HashMap[address, HashMap[uint256, bool]]

admin: public(address)  # Can and will be a smart contract

# events
event SubmitProposal:
    destination: address
    proposal_id: uint256
    requestor: address
    data: bytes32
    remarks: String[100]

event ApproveProposal:
    destination: address
    proposal_id: uint256
    signer: address

event AddSigner:
    new_signer: address
    requestor: address

event RemovedSigner:
    removed_signer: address
    requestor: address

event RevokeProposalapproval:
    destination: address
    revoked_signer: address
    proposal_id: uint256

event ProposalExecuted:
    proposal_id: uint256

@external
def __init__():
    self.admin = msg.sender

@external
def initialise(_signers: DynArray[address, 10], _number_of_approvals: uint256):

    for _signer in _signers:
        if _signer != ZERO_ADDRESS:
            self.signers.append(_signer)
            self.is_signer[_signer] = True

    self.number_of_approvals = _number_of_approvals

@internal
@view
def _get_approver(_requestor: address, _destination: address, _proposal_id: uint256) -> (address, uint256):
    _count: uint256 = 0

    # get index of approver to set it to zero_address
    for _approver in self.proposals[_destination][_proposal_id].approvers:
        if _approver == msg.sender:
            return (_approver, _count)
        _count += 1
    
    return (ZERO_ADDRESS, 0)      

@internal
def _execute_proposal(_destination: address, _proposal_id: uint256):
    assert _destination != ZERO_ADDRESS
    # ensure Proposal has reached number of approvals required.
    assert self.proposals[_destination][_proposal_id].approvals == self.number_of_approvals, 'cannot execute, not enough approvals'

    self.proposals[_destination][_proposal_id].executed = True # dev: setting to true

    if self.proposals[_destination][_proposal_id].method_name_id == 'toggle_pause':
        GuildController(_destination).toggle_pause(convert(self.proposals[_destination][_proposal_id].data, address)) # dev: executing toggle pause
    
    log ProposalExecuted(_proposal_id)

@external
def submit_proposal(_requestor: address, _destination: address, _method_name: String[32], _data: bytes32, _remarks: String[100] = '') -> uint256:
    assert _requestor == msg.sender, 'requestor must be the same as msg.sender'
    assert _requestor != ZERO_ADDRESS, 'requestor must not have empty address'
    assert len(_method_name) != 0

    _id: uint256 = len(self.proposals[_destination])

    self.proposals[_destination].append(Proposal({
        proposal_id: _id,
        executed: False,
        approvals: 0,
        method_name_id: _method_name,
        data: _data,
        destination: _destination,
        requestor: _requestor,
        approvers: [],
        remarks: _remarks
    }))

    log SubmitProposal(_destination, _id, _requestor, _data, _remarks)

    return _id

@external
def approve_proposal(_destination: address, _proposal_id: uint256):
    assert _destination != ZERO_ADDRESS, 'destination address is empty'
    # ensure sender belongs to destination
    assert self.is_signer[msg.sender] == True, 'sender is not a signer'
    # ensure Proposal has not been executed
    assert self.proposals[_destination][_proposal_id].executed == False, 'Proposal has been executed'

    # check if sender has already approved proposal
    _approver: address = ZERO_ADDRESS
    _count: uint256 = 0

    _approver, _count = self._get_approver(msg.sender, _destination, _proposal_id)

    assert _approver == ZERO_ADDRESS, 'sender has already approve proposal'

    self.proposals[_destination][_proposal_id].approvers.append(msg.sender)
    self.proposals[_destination][_proposal_id].approvals += 1

    log ApproveProposal(_destination, _proposal_id, msg.sender)

    # if approval has reached desired threshold, execute proposal. 
    if self.proposals[_destination][_proposal_id].approvals == self.number_of_approvals:
        self._execute_proposal(_destination, _proposal_id)

@external
def revoke_proposal_approval(_destination: address, _proposal_id: uint256):
    assert _destination != ZERO_ADDRESS
    # ensure sender belongs to destination
    assert self.is_signer[msg.sender] == True
    # ensure Proposal exist
    assert self.proposals[_destination][_proposal_id].executed == False, 'Proposal has been executed'

    _approver: address = ZERO_ADDRESS
    _count: uint256 = 0

    _approver, _count = self._get_approver(msg.sender, _destination, _proposal_id)

    assert _approver != ZERO_ADDRESS, 'sender not found in approved approver list'

    self.proposals[_destination][_proposal_id].approvers[_count] = ZERO_ADDRESS

    self.proposals[_destination][_proposal_id].approvals -= 1

    log RevokeProposalapproval(_destination, msg.sender, _proposal_id)

@external
def add_signer(_new_signer: address):
    assert self.is_signer[msg.sender] == True, 'sender must be part of signers to add in new signer'
    assert self.is_signer[_new_signer] == False, 'signer already exist'

    self.signers.append(_new_signer)
    self.is_signer[_new_signer] = True

    log AddSigner(_new_signer, msg.sender)

@external
def remove_signer(_to_be_removed_signer: address):
    assert self.is_signer[msg.sender] == True, 'sender must be part of signers to remove signer'
    assert self.is_signer[_to_be_removed_signer] == True, 'signer does not exist'

    self.is_signer[_to_be_removed_signer] = False

    log RemovedSigner(_to_be_removed_signer, msg.sender)

@external
def set_number_of_approvals(_number_of_approvals: uint256):
    assert self.is_signer[msg.sender] == True, 'sender must be part of signers to number of approval'
    assert _number_of_approvals > 0, 'approval must be more than 0'
    assert _number_of_approvals > self.number_of_approvals, 'current number of approval is larger or equal to intended number'
    
    self.number_of_approvals = _number_of_approvals

@external
def get_proposal_with_proposal_id(_destination: address, _proposal_id: uint256) -> Proposal:
    return self.proposals[_destination][_proposal_id]

@external
def is_proposal_exist_with_method_name(_destination: address, _method_name: String[100]) -> bool:

    for _count in range(1000):
        if self.proposals[_destination][_count].method_name_id == _method_name:
            return True

    return False

@external
@view
def check_status(_requestor: address, _destination: address, _proposal_id: uint256) -> bool:
    return self._get_approver(_requestor, _destination, _proposal_id)[0] != ZERO_ADDRESS