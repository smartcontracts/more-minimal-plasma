from plasma_core.utils.transactions import decode_utxo_position
from plasma_core.utils.address import address_to_hex
from plasma_core.constants import NULL_SIGNATURE
from plasma_core.exceptions import (InvalidBlockSignatureException,
                                    InvalidTxSignatureException,
                                    TxAlreadySpentException,
                                    TxAmountMismatchException)
from plasma_core.transaction import Transaction
from plasma_core.block import Block


class ChildChain(object):
    """Stores an immutable chain of Plasma blocks.

    Attributes:
        operator (bytes): Address of the Plasma operator.
        blocks (dict): Mapping from block numbers to blocks.
        parent_queue (dict): Mapping from block numbers to pending children.
        current_plasma_block_number (int): The current Plasma block number.
    """

    def __init__(self, operator):
        self.operator = operator
        self.blocks = {}
        self.parent_queue = {}
        self.current_plasma_block_number = 1

        self.on('Deposit', self.apply_deposit)
        self.on('ExitStarted', self.apply_exit)
        # self.on('PlasmaBlockRootCommitted', )


    def apply_deposit(self, event):
        """ Creates the initial transaction based on the deposit on the root chain and stores it as a block

        Attributes:
            events (Event): 'Deposit' event being emitted
        """

        event_args = event['args']

        depositor = event_args['owner']
        amount = event_args['amount']
        blknum = event_args['depositBlock']

        # inputs would be default inputs as specified in Transaction
        depositTx = Transaction(
            ouputs=[(depositor, amount), (NULL_ADDRESS, 0)]
        )

        depositBlock = Block([depositTx])
        self.blocks[blknum] = depositBlock

    def apply_exit(self, event):
        """

        Attributes:
            events (Event): 'ExitStarted' event being emitted
        """
        event_args = event['args']
        utxoPos = event_args['utxoPos']
        self.mark_utxo_spent(*self.unpack_utxo_pos(utxoPos))

    def mark_utxo_spent(self, blknum, txindex, oindex):
        if blknum == 0:
            return
        self.blocks[blknum].transactions[txindex].spent[oindex] = True

    # to abstract out into util module
    def unpack_utxo_pos(utxo_pos):
        blknum = utxo_pos // 1000000000
        txindex = (utxo_pos % 1000000000) // 10000
        oindex = utxo_pos - blknum * 1000000000 - txindex * 10000
        return (blknum, txindex, oindex)

    def add_block(self, block):
        """Adds a block to the chain of blocks if it's valid.

        Attributes:
            block (Block): Block to be added.
        """

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
        """Determines whether a transaction is valid.

        Attributes:
            tx (Transaction): Transaction to be validated.
            temp_spent (dict): Optional additional set of spent transactions.
        """

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
        """Returns the block for a given block number.

        Args:
            blknum (int): Block number to query.

        Returns:
            Block: Corresponding block object.
        """

        return self.blocks[blknum]

    def get_transaction(self, transaction_position):
        """Returns the transaction at a given position.

        Args:
            transaction_position (int): Transaction position to query.

        Returns:
            Transaction: Corresponding transaction object.
        """

        (blknum, txindex, _) = decode_utxo_position(transaction_position)
        return self.blocks[blknum].transactions[txindex]

    def _apply_transaction(self, tx):
        """Marks the inputs to a transaction as spent.

        Args:
            tx (Transaction): Transaction to modify.
        """

        for i in tx.inputs:
            if i.blknum == 0:
                continue
            input_tx = self.get_transaction(i.position)
            input_tx.spent[i.oindex] = True

    def _validate_block(self, block):
        """Determines if a block is valid.

        Args:
            block (Block): Block to validate.
        """

        # Check for a valid signature.
        if not block.is_deposit_block and (block.signature == NULL_SIGNATURE or address_to_hex(block.signer) != self.operator):
            raise InvalidBlockSignatureException('failed to validate block')

        for tx in block.transactions:
            self.validate_transaction(tx)

    def _apply_block(self, block):
        """Marks all of the transactions in a block as spent and inserts it.

        Args:
            block (Block): Block to insert.
        """

        for tx in block.transactions:
            self._apply_transaction(tx)
        self.blocks[block.number] = block
