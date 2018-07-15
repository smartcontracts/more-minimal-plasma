from plasma_core.utils.transactions import decode_utxo_position
from plasma_core.utils.address import address_to_hex
from plasma_core.constants import NULL_SIGNATURE
from plasma_core.exceptions import (InvalidBlockSignatureException,
                                    InvalidTxSignatureException,
                                    TxAlreadySpentException,
                                    TxAmountMismatchException)


class ChildChain(object):

    def __init__(self, operator):
        self.operator = operator
        self.blocks = {}
        self.parent_queue = {}
        self.current_plasma_block_number = 1

    def add_block(self, block):
        # Is the block being added to the head?
        if block.number == self.current_plasma_block_number:
            # Validate the block.
            self._validate_block(block)

            # Insert the block into the chain.
            self._apply_block(block)

            # Update the head state.
            self.current_plasma_block_number += 1
        # Or does the block not yet have a parent?
        elif block.number > self.current_plasma_block_number:
            parent_block_number = block.number - 1
            if parent_block_number not in self.parent_queue:
                self.parent_queue[parent_block_number] = []
            self.parent_queue[parent_block_number].append(block)
            return False
        # Block already exists.
        else:
            return False

        # Process any blocks that were waiting for this block.
        if block.number in self.parent_queue:
            for blk in self.parent_queue[block.number]:
                self.add_block(blk)
            del self.parent_queue[block.number]
        return True

    def validate_transaction(self, tx, temp_spent={}):
        input_amount = 0
        output_amount = sum([o.amount for o in tx.outputs])

        for i in range(len(tx.inputs)):
            tx_input = tx.inputs[i]

            # Transactions coming from block 0 are valid.
            if tx_input.blknum == 0:
                continue

            input_tx = self.get_transaction(tx_input.position)
            input_amount += input_tx.outputs[tx_input.oindex].amount

            if tx.signatures[i] == NULL_SIGNATURE or tx.signers[i] != input_tx.outputs[tx_input.oindex].owner:
                raise InvalidTxSignatureException('failed to validate tx')

            # Check to see if the input is already spent.
            if input_tx.spent[tx_input.oindex] or tx_input.position in temp_spent:
                raise TxAlreadySpentException('failed to validate tx')

        if not tx.is_deposit and input_amount < output_amount:
            raise TxAmountMismatchException('failed to validate tx')

    def get_block(self, blknum):
        return self.blocks[blknum]

    def get_transaction(self, transaction_id):
        (blknum, txindex, _) = decode_utxo_position(transaction_id)
        return self.blocks[blknum].transactions[txindex]

    def get_current_block_num(self):
        return self.current_plasma_block_number

    def _apply_transaction(self, tx):
        for i in tx.inputs:
            if i.blknum == 0:
                continue
            input_tx = self.get_transaction(i.position)
            input_tx.spent[i.oindex] = True

    def _validate_block(self, block):
        # Check for a valid signature.
        if not block.is_deposit_block and (block.signature == NULL_SIGNATURE or address_to_hex(block.signer) != self.operator):
            raise InvalidBlockSignatureException('failed to validate block')

        for tx in block.transactions:
            self.validate_transaction(tx)

    def _apply_block(self, block):
        for tx in block.transactions:
            self._apply_transaction(tx)
        self.blocks[block.number] = block
