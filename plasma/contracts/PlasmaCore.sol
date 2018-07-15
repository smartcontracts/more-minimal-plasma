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
        TransactionInput[2] inputs;
        TransactionOutput[2] outputs;
    }

    
    /*
     * Internal functions
     */

    /**
     * @dev Decodes an RLP encoded transaction.
     * @param _tx RLP encoded transaction.
     * @return Decoded transaction.
     */
    function decode(bytes memory _tx) internal pure returns (Transaction) {
        RLP.RLPItem[] memory txList = _tx.toRLPItem().toList();
        RLP.RLPItem[] memory inputs = txList[0].toList();
        RLP.RLPItem[] memory outputs = txList[1].toList();

        Transaction memory decodedTx;
        for (uint i = 0; i < 2; i++) {
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
     * @dev Given a UTXO position, returns the block number.
     * @param _utxoPosition UTXO position to decode.
     * @return The output's block number.
     */
    function getBlknum(uint256 _utxoPosition) internal pure returns (uint256) {
        return _utxoPosition / BLOCK_OFFSET;
    }

    /**
     * @dev Given a UTXO position, returns the transaction index.
     * @param _utxoPosition UTXO position to decode.
     * @return The output's transaction index.
     */
    function getTxindex(uint256 _utxoPosition) internal pure returns (uint256) {
        return (_utxoPosition % BLOCK_OFFSET) / TX_OFFSET;
    }

    /**
     * @dev Given a UTXO position, returns the output index.
     * @param _utxoPosition UTXO position to decode.
     * @return The output's index.
     */
    function getOindex(uint256 _utxoPosition) internal pure returns (uint8) {
        return uint8(_utxoPosition % TX_OFFSET);
    }

    /**
     * @dev Calculates a deposit root given an encoded deposit transaction.
     * @param _encodedDepositTx RLP encoded deposit transaction.
     * @param _treeHeight Height of the Merkle tree.
     * @return The deposit root.
     */
    function getDepositRoot(bytes _encodedDepositTx, uint256 _treeHeight) internal pure returns (bytes32) {
        bytes32 root = keccak256(_encodedDepositTx);
        bytes32 zeroHash = keccak256(abi.encodePacked(uint256(0)));
        for (uint256 i = 0; i < _treeHeight; i++) {
            root = keccak256(abi.encodePacked(root, zeroHash));
            zeroHash = keccak256(abi.encodePacked(zeroHash, zeroHash));
        }
        return root;
    }

    function validateSignatures(bytes32 _txHash, bytes _signatures, bytes _confirmationSignatures) returns (bool) {
        require(_signatures.length % 65 == 0);
        require(_signatures.length == _confirmationSignatures.length);

        for (uint256 offset = 0; offset < signatures.length; offset += 65) {
            bytes memory signature = ByteUtils.slice(_signatures, offset, 65);
            bytes memory confirmationSigature = ByteUtils.slice(_confirmationSignatures, offset, 65);
            if (ECRecovery.recover(_txHash, signature) != ECRecovery.recover(keccak256(_txHash, confirmationSigature)) {
                return false;
            }
        }

        return true;
    }
}
