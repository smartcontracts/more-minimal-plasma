pragma solidity ^0.4.0;

import "./Math.sol";
import "./Merkle.sol";
import "./PlasmaCore.sol";
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

    function deposit(bytes _encodedDepositTx) public payable {
        plasmaBlockRoots[currentPlasmaBlockNumber] = PlasmaBlockRoot({
            root: PlasmaCore.getDepositRoot(_encodedDepositTx, TREE_HEIGHT),
            timestamp: block.timestamp
        });

        emit DepositCreated(msg.sender, msg.value, currentPlasmaBlockNumber);
        currentPlasmaBlockNumber = currentPlasmaBlockNumber.add(1);
    }

    function commitPlasmaBlockRoot(bytes32 _root) public onlyOperator {
        plasmaBlockRoots[currentPlasmaBlockNumber] = PlasmaBlockRoot({
            root: _root,
            timestamp: block.timestamp
        });

        emit PlasmaBlockRootCommitted(currentPlasmaBlockNumber, _root);
        currentPlasmaBlockNumber = currentPlasmaBlockNumber.add(1);
    }

    function startExit(
        uint256 _utxoPosition,
        bytes _encodedTx,
        bytes _txInclusionProof,
        bytes _txSignatures,
        bytes _txConfirmationSignatures
    ) public payable onlyWithValue(EXIT_BOND) {
        uint256 blockNumber = PlasmaCore.getBlockNumber(_utxoPosition);
        uint256 txIndex = PlasmaCore.getTxIndex(_utxoPosition);
        uint256 outputIndex = PlasmaCore.getOutputIndex(_utxoPosition);

        PlasmaCore.TransactionOutput memory transactionOutput = PlasmaCore.decodeTx(_encodedTx).outputs[outputIndex];

        require(transactionOutput.owner == msg.sender);

        PlasmaBlockRoot memory plasmaBlockRoot = plasmaBlockRoots[blockNumber];
        bytes32 txHash = keccak256(_encodedTx);

        require(Merkle.checkMembership(txHash, txIndex, plasmaBlockRoot.root, _txInclusionProof));
        require(PlasmaCore.validateSignatures(txHash, _txSignatures, _txConfirmationSignatures));
        require(transactionOutput.amount > 0);
        require(plasmaExits[_utxoPosition].amount == 0);

        uint256 exitableAt = Math.max(plasmaBlockRoot.timestamp + 2 weeks, block.timestamp + 1 weeks);
        exitQueue.insert(exitableAt, _utxoPosition);
        plasmaExits[_utxoPosition] = PlasmaExit({
            owner: transactionOutput.owner,
            amount: transactionOutput.amount
        });

        emit ExitStarted(msg.sender, _utxoPosition, transactionOutput.amount);
    }

    function getCount() public constant returns(uint count) 
    {
    return array.length;
    }

    function challengeExit(
        uint256 _exitingUtxoPosition,
        uint256 _spendingTxPosition,
        bytes _encodedSpendingTx,
        bytes _spendingTxConfirmationSignature

    ) public {
        PlasmaCore.Transaction memory transaction = PlasmaCore.decodeTx(_encodedSpendingTx);
        bool spendsExitingUtxo = false;
        for (uint8 i = 0; i < transaction.inputs.length; i++) {
            if (_exitingUtxoPosition == PlasmaCore.getInputPosition(transaction.inputs[i])) {
                spendsExitingUtxo = True;
                break;
            }
        }
        require(spendsExitingUtxo);

        // Validate the confirmation signature.
        bytes confirmationHash = keccak256(keccak256(_encodedSpendingTx));
        address owner = exits[_exitingUtxoPosition].owner;
        require(owner == ECRecovery.recover(confirmationHash, _spendingTxConfirmationSignatures));

        // Delete the owner but keep the amount to prevent double exits.
        delete exits[_exitingUtxoPosition].owner;
    }

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
