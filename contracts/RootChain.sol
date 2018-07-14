pragma solidity ^0.4.0;

import "./PlasmaCore.sol";
import "./PriorityQueue.sol";


/**
 * @title RootChain
 * @dev Plasma Battleship root chain contract implementation. 
 */
contract RootChain {
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
    }


    /*
     * Public functions
     */

    function deposit(bytes _encodedDepositTx) public {

    }

    function commitPlasmaBlockRoot(bytes32 _root) public onlyOperator {
        plasmaBlockRoots[currentPlasmaBlockNumber] = PlasmaBlockRoot({
            root: _root,
            timestamp: block.timestamp});

        emit PlasmaBlockRootCommitted(currentPlasmaBlockNumber, _root);

        currentPlasmaBlockNumber++;
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
