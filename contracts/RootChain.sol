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

    /*
    * Assumes that only ETH tokens will be used. We get the exit with the highest priority in the queue and split it because each exit is a concatenation of utxopos and timestamp.
    */
    function processExits()
        public
    {
        uint256 utxoPos;
        uint256 exitable_at;
        (utxoPos, exitable_at) = getNextExit();
        PlasmaExit memory currentExit = plasmaExits[utxoPos];

        while(exitable_at < block.timestamp){
            currentExit = plasmaExits[utxoPos];
            currentExit.owner.transfer(currentExit.amount);
            exitQueue.delMin();
            
            //Delete owner but keep amount to prevent another exit with the same utxoPos
            delete plasmaExits[utxoPos].owner;
            if (exitQueue.currentSize() > 0){
                (utxoPos, exitable_at) = getNextExit();
            } else {
                return;
            }
        }

    }

    function getNextExit()
        public
        view
        returns (uint256, uint256)
    {
        uint256 highestPriority = exitQueue.getMin();
        uint256 utxoPos = uint256(uint128(highestPriority));
        uint256 exitable_at = highestPriority>>128;
        return (utxoPos, exitable_at);
    }
}
