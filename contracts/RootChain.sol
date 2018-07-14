pragma solidity ^0.4.0;


/**
 * @title RootChain
 * @dev Plasma Battleship root chain contract implementation. 
 */
contract RootChain {
    /*
     * Storage
     */

    address public operator;

    
    /*
     * Constructor
     */

    constructor() public {
        operator = msg.sender;
    }
}
