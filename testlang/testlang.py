from ethereum.utils import sha3
from plasma_core.child_chain import ChildChain
from plasma_core.account import EthereumAccount
from plasma_core.block import Block
from plasma_core.transaction import Transaction
from plasma_core.constants import NULL_ADDRESS
from plasma_core.utils.signatures import sign
from plasma_core.utils.transactions import decode_utxo_position, encode_utxo_position
from plasma_core.utils.address import address_to_hex


class PlasmaExit(object):
    """Represents a Plasma exit.

    Attributes:
        owner (str): Address of the exit's owner.
        amount (int): How much value is being exited.
    """

    def __init__(self, owner, amount):
        self.owner = owner
        self.amount = amount


class PlasmaBlock(object):
    """Represents a Plasma block.

    Attributes:
        root (str): Root hash of the block.
        timestamp (int): Time when the block was created.
    """

    def __init__(self, root, timestamp):
        self.root = root
        self.timestamp = timestamp


class TestingLanguage(object):
    """Represents the testing language.

    Attributes:
        root_chain (ABIContract): Root chain contract instance.
        eththester (tester): Ethereum tester instance.
        accounts (EthereumAccount[]): List of available accounts.
        operator (EthereumAccount): The operator's account.
        child_chain (ChildChain): Child chain instance.
        confirmations (dict): A mapping from transaction IDs to confirmation signatures.
    """

    def __init__(self, root_chain, ethtester):
        self.root_chain = root_chain
        self.ethtester = ethtester
        self.accounts = ethtester.accounts
        self.operator = self.accounts[0]
        self.child_chain = ChildChain(self.accounts[0].address)

    @property
    def timestamp(self):
        """Current chain timestamp"""
        return self.ethtester.chain.head_state.timestamp

    @property
    def current_plasma_block_number(self):
        """Current block number"""
        return self.root_chain.currentPlasmaBlockNumber()

    def commit_plasma_block_root(self, block, signer=None):
        """Commits a Plasma block root to Ethereum.

        Args:
            block (Block): Block to be committed.
            signer (EthereumAccount): Account to commit the root.
        """

        signer = signer or self.operator
        block.sign(signer.key)
        self.root_chain.commitPlasmaBlockRoot(block.root, sender=signer.key)
        self.child_chain.add_block(block)

    def deposit(self, owner, amount):
        """Creates a deposit transaction for a given owner and amount.

        Args:
            owner (EthereumAccount): Account to own the deposit.
            amount (int): Deposit amount.

        Returns:
            int: Unique identifier of the deposit.
        """

        deposit_tx = Transaction(inputs=[], outputs=[(owner.address, amount)])
        blknum = self.root_chain.currentPlasmaBlockNumber()
        self.root_chain.deposit(deposit_tx.encoded, value=amount, sender=owner.key)

        block = Block(transactions=[deposit_tx], number=blknum)
        self.child_chain.add_block(block)
        return blknum

    def spend_utxo(self, utxo_position, new_owner, amount, signer):
        """Creates a spending transaction and inserts it into the chain.

        Args:
            utxo_position (int): Identifier of the UTXO to spend.
            new_owner (EthereumAccount): Account to own the output of this spend.
            amount (int): Amount to spend.
            signer (EthereumAccount): Account to sign this transaction.

        Returns:
            int: Unique identifier of the spend.
        """

        spend_tx = Transaction(inputs=[decode_utxo_position(utxo_position)], outputs=[(new_owner.address, amount)])
        spend_tx.sign(0, signer.key)

        blknum = self.root_chain.currentPlasmaBlockNumber()
        block = Block(transactions=[spend_tx], number=blknum)
        self.commit_plasma_block_root(block)
        return encode_utxo_position(blknum, 0, 0)

    def confirm(self, tx_position, index, signer):
        """Signs a confirmation signature for a spend.

        Args:
            tx_position (int): Identifier of the transaction.
            index (int): Index of the input to confirm.
            signer (EthereumAccount): Account to sign this confirmation.
        """

        spend_tx = self.child_chain.get_transaction(tx_position)
        spend_tx.confirm(index, signer.key)

    def start_exit(self, owner, utxo_position):
        """Starts a standard exit.

        Args:
            owner (EthereumAccount): Account to attempt the exit.
            utxo_position (int): Position of the UTXO to be exited.
        """

        bond = self.root_chain.EXIT_BOND()
        self.root_chain.startExit(utxo_position, *self.get_exit_proof(utxo_position), sender=owner.key, value=bond)

    def get_exit_proof(self, utxo_position):
        (blknum, _, _) = decode_utxo_position(utxo_position)
        block = self.child_chain.get_block(blknum)

        spend_tx = self.child_chain.get_transaction(utxo_position)
        encoded_tx = spend_tx.encoded
        proof = block.merkle.create_membership_proof(spend_tx.encoded)
        signatures = spend_tx.joined_signatures
        confirmation_signatures = spend_tx.joined_confirmations
        return (encoded_tx, proof, signatures, confirmation_signatures)

    def challenge_exit(self, exiting_utxo_position, spending_tx_position):
        """Challenges an exit with a double spend.

        Args:
            exiting_utxo_position (int): Position of the UTXO being exited.
            spending_tx_position (int): Position of the transaction that spent the UTXO.
        """

        self.root_chain.challengeExit(exiting_utxo_position, spending_tx_position, *self.get_challenge_proof(exiting_utxo_position, spending_tx_position))

    def process_exits(self):
        """Processes any exits that have completed the exit period"""

        self.root_chain.processExits(NULL_ADDRESS)

    def get_challenge_proof(self, exiting_utxo_position, spending_tx_position):
        """Returns information required to submit a challenge.

        Args:
            exiting_utxo_position (int): Position of the UTXO being exited.
            spending_tx_position (int): Position of the transaction that spent the UTXO.

        Returns:
            int, bytes, bytes, bytes, bytes: Information necessary to create a challenge proof.
        """

        spend_tx = self.child_chain.get_transaction(spending_tx_position)
        (blknum, _, _) = decode_utxo_position(spending_tx_position)
        block = self.child_chain.blocks[blknum]
        proof = block.merkle.create_membership_proof(spend_tx.merkle_hash)
        signatures = b''.join(spend_tx.signatures)
        confirmation_signatures = b''.join(spend_tx.confirmations)
        return (spend_tx.encoded, proof, signatures, confirmation_signatures)

    def get_plasma_block(self, blknum):
        """Queries a plasma block by its number.

        Args:
            blknum (int): Plasma block number to query.

        Returns:
            PlasmaBlock: Formatted plasma block information.
        """

        block_info = self.root_chain.plasmaBlockRoots(blknum)
        return PlasmaBlock(*block_info)

    def get_plasma_exit(self, utxo_position):
        """Queries a plasma exit by its position in the chain.

        Args:
            utxo_position (int): Identifier of the exit to query.

        Returns:
            PlasmaExit: Formatted plasma exit information.
        """

        exit_info = self.root_chain.plasmaExits(utxo_position)
        return PlasmaExit(*exit_info)

    def get_balance(self, account):
        """Queries the balance of an account.

        Args:
            account (EthereumAccount): Account to query,

        Returns:
            int: The account's balance.
        """

        return self.ethtester.chain.head_state.get_balance(account.address)

    def forward_timestamp(self, amount):
        """Forwards the chain's timestamp.

        Args:
            amount (int): Number of seconds to move forward time.
        """

        self.ethtester.chain.head_state.timestamp += amount
