pragma solidity ^0.4.0;

import "./Math.sol";
import "./Merkle.sol";
import "./PlasmaUtils.sol";
import "./PriorityQueue.sol";


/**
 * @title RootChain
 * @dev Plasma Battleship root chain contract implementation.
 */
contract RootChain {
    using SafeMath for uint256;

    /*
     * Events
     */

    event DepositCreated(
        address indexed owner,
        uint256 amount,
        uint256 depositBlock
    );

    event PlasmaBlockRootCommitted(
        uint256 blockNumber,
        bytes32 root
    );

    event ExitStarted(
        address indexed owner,
        uint256 utxoPosition,
        uint256 amount
    );


    /*
     * Storage
     */

    uint256 constant public CHALLENGE_PERIOD = 1 weeks;
    uint256 constant public EXIT_BOND = 123456789;
    uint256 constant public TREE_HEIGHT = 10; // Maximum number of transactions per block is set at 1024, so maximum tree height is 10.

    PriorityQueue exitQueue;
    uint256 public currentPlasmaBlockNumber;
    address public operator;

    mapping (uint256 => PlasmaBlockRoot) public plasmaBlockRoots;
    mapping (uint256 => PlasmaExit) public plasmaExits;

    struct PlasmaBlockRoot {
        bytes32 root;
        uint256 timestamp;
    }

    struct PlasmaExit {
        address owner;
        uint256 amount;
    }


    /*
     * Modifiers
     */

    modifier onlyOperator() {
        require(msg.sender == operator);
        _;
    }

    modifier onlyWithValue(uint256 value) {
        require(msg.value == value);
        _;
    }


    /*
     * Constructor
     */

    constructor() public {
        operator = msg.sender;
        currentPlasmaBlockNumber = 1;
        exitQueue = new PriorityQueue();
    }


    /*
     * Public functions
     */

    /**
     * @dev Allows a user to deposit into the Plasma chain.
     * @param _encodedDepositTx RLP encoded deposit transaction to be inserted into a block.
     */
    function deposit(bytes _encodedDepositTx) public payable {
        PlasmaUtils.Transaction memory transaction = PlasmaUtils.decodeTx(_encodedDepositTx);

        // First output should be the value of this transaction.
        require(transaction.outputs[0].amount == msg.value);

        // Second output should be unused.
        require(transaction.outputs[1].amount == 0);

        plasmaBlockRoots[currentPlasmaBlockNumber] = PlasmaBlockRoot({
            root: PlasmaUtils.getDepositRoot(_encodedDepositTx, TREE_HEIGHT),
            timestamp: block.timestamp
        });

        emit DepositCreated(msg.sender, msg.value, currentPlasmaBlockNumber);
        currentPlasmaBlockNumber = currentPlasmaBlockNumber.add(1);
    }

    /**
     * @dev Allows the operator to commit a block root to Ethereum.
     * @param _root Root to be committed.
     */
    function commitPlasmaBlockRoot(bytes32 _root) public onlyOperator {
        plasmaBlockRoots[currentPlasmaBlockNumber] = PlasmaBlockRoot({
            root: _root,
            timestamp: block.timestamp
        });

        emit PlasmaBlockRootCommitted(currentPlasmaBlockNumber, _root);
        currentPlasmaBlockNumber = currentPlasmaBlockNumber.add(1);
    }

    /**
     * @dev Starts an exit for a given UTXO.
     * @param _utxoPosition Position of the UTXO in the Plasma chain (based on block number, transaction index, output index)
     * @param _encodedTx RLP encoded transaction that created the output.
     * @param _txInclusionProof Proof that the transaction was included in the Plasma chain.
     * @param _txSignatures Signatures that prove the transaction is valid.
     * @param _txConfirmationSignatures Signatures that attest the transaction was included in a valid block.
     */
    function startExit(
        uint256 _utxoPosition,
        bytes _encodedTx,
        bytes _txInclusionProof,
        bytes _txSignatures,
        bytes _txConfirmationSignatures
    ) public payable onlyWithValue(EXIT_BOND) {
        uint256 blockNumber = PlasmaUtils.getBlockNumber(_utxoPosition);
        uint256 txIndex = PlasmaUtils.getTxIndex(_utxoPosition);
        uint256 outputIndex = PlasmaUtils.getOutputIndex(_utxoPosition);

        PlasmaUtils.TransactionOutput memory transactionOutput = PlasmaUtils.decodeTx(_encodedTx).outputs[outputIndex];

        // Only the output owner should be able to start an exit.
        require(transactionOutput.owner == msg.sender);

        // Don't allow zero-value outputs to exit.
        require(transactionOutput.amount > 0);

        // Check that this UTXO hasn't already started an exit.
        require(plasmaExits[_utxoPosition].amount == 0);

        // Validate the transaction.
        PlasmaBlockRoot memory plasmaBlockRoot = plasmaBlockRoots[blockNumber];
        bytes32 txHash = keccak256(_encodedTx);
        require(Merkle.checkMembership(txHash, txIndex, plasmaBlockRoot.root, _txInclusionProof));
        require(PlasmaUtils.validateSignatures(txHash, _txSignatures, _txConfirmationSignatures));

        // Must wait at least one week (> 1 week old UTXOs), but might wait up to two weeks (< 1 week old UTXOs).
        uint256 exitableAt = Math.max(plasmaBlockRoot.timestamp + 2 weeks, block.timestamp + 1 weeks);

        exitQueue.insert(exitableAt, _utxoPosition);
        plasmaExits[_utxoPosition] = PlasmaExit({
            owner: transactionOutput.owner,
            amount: transactionOutput.amount
        });

        emit ExitStarted(msg.sender, _utxoPosition, transactionOutput.amount);
    }

    /**
     * @dev Blocks an exiting UTXO by proving the UTXO was spent.
     * @param _exitingUtxoPosition Position of the UTXO being exited.
     * @param _encodedSpendingTx RLP encoded transaction that spent the UTXO.
     * @param _spendingTxConfirmationSignature Confirmation signature over the spending transaction.
     */
    function challengeExit(
        uint256 _exitingUtxoPosition,
        bytes _encodedSpendingTx,
        bytes _spendingTxConfirmationSignature
    ) public {
        PlasmaUtils.Transaction memory transaction = PlasmaUtils.decodeTx(_encodedSpendingTx);

        // Check that the exiting UTXO was actually spent.
        bool spendsExitingUtxo = false;
        for (uint8 i = 0; i < transaction.inputs.length; i++) {
            if (_exitingUtxoPosition == PlasmaUtils.getInputPosition(transaction.inputs[i])) {
                spendsExitingUtxo = true;
                break;
            }
        }
        require(spendsExitingUtxo);

        // Validate the confirmation signature.
        bytes32 confirmationHash = keccak256(abi.encodePacked(keccak256(_encodedSpendingTx)));
        address owner = plasmaExits[_exitingUtxoPosition].owner;
        require(owner == ECRecovery.recover(confirmationHash, _spendingTxConfirmationSignature));

        // Delete the owner but keep the amount to prevent double exits.
        delete plasmaExits[_exitingUtxoPosition].owner;
    }

    /**
     * @dev Processes any exits that have completed the exit period.
     */
    function processExits() public {
        uint256 exitableAt;
        uint256 utxoPosition;

        // Iterate while the queue is not empty.
        while(exitQueue.currentSize() > 0){
            (exitableAt, utxoPosition) = exitQueue.getMin();

            // Check if this exit has finished its challenge period.
            if (exitableAt > block.timestamp){
                return;
            }

            PlasmaExit memory currentExit = plasmaExits[utxoPosition];

            // If an exit was successfully challenged, owner would be address(0).
            if (currentExit.owner != address(0)){
                currentExit.owner.transfer(currentExit.amount);

                // Delete owner but keep amount to prevent another exit from the same UTXO.
                delete plasmaExits[utxoPosition].owner;
            }

            exitQueue.delMin();
        }
    }
}
