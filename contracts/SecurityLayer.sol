pragma solidity ^0.8.0;

contract SecurityLayer {
    address public owner;  // Wallet owner
    address public secondaryApprover;  // Secondary device for 2FA
    mapping(address => bool) public approvedDestinations;  // Whitelisted addresses
    uint256 public dailyLimit;  // Daily transaction limit (in wei)
    uint256 public dailySpent;  // Amount spent today
    uint256 public lastReset;  // Last reset timestamp
    bool public locked;  // Killswitch status
    mapping(bytes32 => bool) public pendingTransactions;  // Pending 2FA transactions

    event TransactionRequested(bytes32 txHash, address to, uint256 value);
    event TransactionApproved(bytes32 txHash);
    event TransactionRejected(bytes32 txHash);
    event WalletLocked();
    event WalletUnlocked();

    modifier onlyOwner() {
        require(msg.sender == owner, "Not owner");
        _;
    }

    modifier onlySecondaryApprover() {
        require(msg.sender == secondaryApprover, "Not secondary approver");
        _;
    }

    modifier notLocked() {
        require(!locked, "Wallet is locked");
        _;
    }

    constructor(address _secondaryApprover, uint256 _dailyLimit) {
        owner = msg.sender;
        secondaryApprover = _secondaryApprover;
        dailyLimit = _dailyLimit;
        lastReset = block.timestamp;
        locked = false;
    }

    // Reset daily spent amount if 24 hours have passed
    function resetDailySpent() internal {
        if (block.timestamp >= lastReset + 1 days) {
            dailySpent = 0;
            lastReset = block.timestamp;
        }
    }

    // Request a transaction (initiates 2FA)
    function requestTransaction(address to, uint256 value) external onlyOwner notLocked {
        resetDailySpent();
        require(dailySpent + value <= dailyLimit, "Exceeds daily limit");
        require(value > 0, "Value must be greater than 0");

        // Check if destination is whitelisted
        if (!approvedDestinations[to]) {
            bytes32 txHash = keccak256(abi.encodePacked(to, value, block.timestamp));
            pendingTransactions[txHash] = true;
            emit TransactionRequested(txHash, to, value);
        } else {
            // Auto-approve for whitelisted addresses
            dailySpent += value;
            payable(to).transfer(value);
        }
    }

    // Approve a transaction (2FA step)
    function approveTransaction(bytes32 txHash) external onlySecondaryApprover notLocked {
        require(pendingTransactions[txHash], "Transaction not pending");
        pendingTransactions[txHash] = false;
        emit TransactionApproved(txHash);
        // Extract transaction details and execute (simplified for demo)
        // In a real implementation, store to/value in a mapping and execute here
    }

    // Reject a transaction
    function rejectTransaction(bytes32 txHash) external onlySecondaryApprover {
        require(pendingTransactions[txHash], "Transaction not pending");
        pendingTransactions[txHash] = false;
        emit TransactionRejected(txHash);
    }

    // Add a whitelisted destination
    function whitelistDestination(address destination) external onlyOwner {
        approvedDestinations[destination] = true;
    }

    // Lock the wallet (killswitch)
    function lockWallet() external onlyOwner {
        locked = true;
        emit WalletLocked();
    }

    // Unlock the wallet
    function unlockWallet() external onlyOwner {
        locked = false;
        emit WalletUnlocked();
    }

    // Receive ETH
    receive() external payable {}
}