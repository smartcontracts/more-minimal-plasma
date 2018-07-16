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

        uint256 exitableAt = Math.max(plasmaBlockRoot.timestamp + 2 weeks, block.timestamp + 1 weeks);
        exitQueue.insert(exitableAt, _utxoPosition);
        plasmaExits[_utxoPosition] = PlasmaExit({
            owner: transactionOutput.owner,
            amount: transactionOutput.amount
        });

        emit ExitStarted(msg.sender, _utxoPosition, transactionOutput.amount);
    }


    function challengeExit(
        uint256 _exitingUtxoPosition,
        uint256 _spendingTxPosition,
        bytes _encodedSpendingTx,
        bytes _spendingTxInclusionProof,
        bytes _spendingTxSignatures,
        bytes _spendingTxConfirmationSignatures
    ) public {

    }

    function processExits() public {

    }
}
