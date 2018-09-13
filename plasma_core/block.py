import rlp
from rlp.sedes import binary, CountableList, big_endian_int
from ethereum import utils
from plasma_core.constants import NULL_SIGNATURE
from plasma_core.transaction import Transaction
from plasma_core.fixed_merkle import FixedMerkle
from plasma_core.utils.signatures import sign, get_signer


class Block(rlp.Serializable):
    """Represents a Plasma block.

    Attributes:
        transactions (Transaction[]): List of transactions in this block.
        number (int): This block's number.
        signature (bytes): Signature on this block.
    """

    fields = [
        ('transactions', CountableList(Transaction)),
        ('number', big_endian_int),
        ('signature', binary),
    ]

    def __init__(self, transactions=[], number=0, signature=NULL_SIGNATURE):
        self.transactions = transactions
        self.number = number
        self.signature = signature

    @property
    def hash(self):
        """Hash of the RLP encoding of this block"""
        return utils.sha3(self.encoded)

    @property
    def signer(self):
        """Address of the signer of this block"""
        return get_signer(self.hash, self.signature)

    @property
    def root(self):
        """Root of this block's Merkle tree"""
        return self.merkle.root

    @property
    def merkle(self):
        """Merkle tree from the list of transactions"""
        return FixedMerkle(10, [tx.merkle_leaf_data for tx in self.transactions])

    @property
    def encoded(self):
        """RLP encoded representation of this block"""
        return rlp.encode(self, UnsignedBlock)

    @property
    def is_deposit_block(self):
        """Whether or not this is a deposit block"""
        return len(self.transactions) == 1 and self.transactions[0].is_deposit

    def sign(self, key):
        """Sets the signature for this block.

        Args:
            key (bytes): Private key to be used to sign.
        """

        self.signature = sign(self.hash, key)


class UnsignedBlock(rlp.Serializable):

    fields = Block.fields[:-1]
