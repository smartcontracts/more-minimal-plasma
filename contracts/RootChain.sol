pragma solidity ^0.4.0;

import "./PlasmaCore.sol";
import "./PriorityQueue.sol";


/**
 * @title RootChain
 * @dev Plasma Battleship root chain contract implementation.
 */
contract RootChain {
    using SafeMath for uint256;
    using PlasmaCore for uint256;
    using PlasmaCore for bytes;


    /*
     * Events
     */

    event DepositCreated(
        address indexed owner,
        uint256 amount,
        uint256 depositBlock
    );

    event BlockSubmitted(
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
    /*
     * Maximum number of transactions per block is set at 1024, so maximum block height would be 10.
     */
    uint256 constant public BLOCK_HEIGHT = 10;

    PriorityQueue exitQueue;
    uint256 public currentBlockNumber;
    address public operator;

    mapping (uint256 => PlasmaBlock) public plasmaBlocks;
    mapping (uint256 => PlasmaExit) public plasmaExits;

    struct PlasmaBlock {
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
    }


    /*
     * Public functions
     */

    function deposit(bytes _encodedDepositTx)
        public
        payable
    {
        //TODO: use library to calculate merkle root
        bytes32 root = "gonna be calculated";
        plasmaBlocks[currentBlockNumber] = PlasmaBlock({
            root: root,
            timestamp: block.timestamp
        });

        emit DepositCreated(msg.sender, msg.value, currentBlockNumber);
        currentBlockNumber = currentBlockNumber.add(1);
    }

    function submitBlock(bytes32 _root) public onlyOperator {

    }

    function startExit(
        uint256 _utxoPosition,
        bytes _encodedTx,
        bytes _txInclusionProof,
        bytes _txSignatures
    ) public onlyWithValue(EXIT_BOND) {

    }

    function challengeExit(
        uint256 _exitingUtxoPosition,
        uint256 _spendingTxPosition,
        uint256 _encodedSpendingTx,
        uint256 _spendingTxInclusionProof,
        uint256 _spendingTxSignatures,
        uint256 _spendingTxConfirmationSignatures
    ) public {

    }

    function processExits() public {

    }
}
