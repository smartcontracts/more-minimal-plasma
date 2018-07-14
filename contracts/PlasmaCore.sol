pragma solidity ^0.4.0;

import "./RLP.sol";


/**
 * @title PlasmaCore
 * @dev Utilities for working with and decoding Plasma MVP transactions.
 */
library PlasmaCore {
    using RLP for bytes;
    using RLP for RLP.RLPItem;


    /*
     * Storage
     */

    uint256 constant internal BLOCK_OFFSET = 1000000000;
    uint256 constant internal TX_OFFSET = 10000;

    struct TransactionInput {
        uint256 blknum;
        uint256 txindex;
        uint256 oindex;
    }

    struct TransactionOutput {
        address owner;
        uint256 amount;
    }

    struct Transaction {
        TransactionInput[4] inputs;
        TransactionOutput[4] outputs;
    }

    
    /*
     * Internal functions
     */
    
    /**
     * @dev Decodes an RLP encoded transaction.
     * @param _tx RLP encoded transaction.
     * @return Decoded transaction.
     */
    function decode(bytes memory _tx)
        internal
        view
        returns (Transaction)
    {
        RLP.RLPItem[] memory txList = _tx.toRLPItem().toList();
        RLP.RLPItem[] memory inputs = txList[0].toList();
        RLP.RLPItem[] memory outputs = txList[1].toList();

        Transaction memory decodedTx;
        for (uint i = 0; i < 4; i++) {
            RLP.RLPItem[] memory input = inputs[i].toList();
            decodedTx.inputs[i] = TransactionInput({
                blknum: input[0].toUint(),
                txindex: input[1].toUint(),
                oindex: input[2].toUint()
            });

            RLP.RLPItem[] memory output = outputs[i].toList();
            decodedTx.outputs[i] = TransactionOutput({
                owner: output[0].toAddress(),
                amount: output[1].toUint()
            });
        }

        return decodedTx;
    }

    /**
     * @dev Given an output ID, returns the block number.
     * @param _outputId Output identifier to decode.
     * @return The output's block number.
     */
    function getBlknum(uint256 _outputId)
        internal
        pure
        returns (uint256)
    {
        return _outputId / BLOCK_OFFSET;
    }

    /**
     * @dev Given an output ID, returns the transaction index.
     * @param _outputId Output identifier to decode.
     * @return The output's transaction index.
     */
    function getTxindex(uint256 _outputId)
        internal
        pure
        returns (uint256)
    {
        return (_outputId % BLOCK_OFFSET) / TX_OFFSET;
    }

    /**
     * @dev Given an output ID, returns the output index.
     * @param _outputId Output identifier to decode.
     * @return The output's index.
     */
    function getOindex(uint256 _outputId)
        internal
        pure
        returns (uint8)
    {
        return uint8(_outputId % TX_OFFSET);
    }
}
