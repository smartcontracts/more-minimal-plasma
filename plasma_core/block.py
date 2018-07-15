import rlp
from rlp.sedes import binary, CountableList, big_endian_int
from ethereum import utils
from plasma_core.constants import NULL_SIGNATURE
from plasma_core.transaction import Transaction
from plasma_core.fixed_merkle import FixedMerkle
from plasma_core.utils.signatures import sign, get_signer


class Block(rlp.Serializable):

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
        return utils.sha3(self.encoded)

    @property
    def signer(self):
        return get_signer(self.hash, self.signature)

    @property
    def root(self):
        return self.merkle.root

    @property
    def merkle(self):
        return FixedMerkle(10, [tx.encoded for tx in self.transactions])

    @property
    def encoded(self):
        return rlp.encode(self, UnsignedBlock)

    @property
    def is_deposit_block(self):
        return len(self.transactions) == 1 and self.transactions[0].is_deposit

    def sign(self, key):
        self.signature = sign(self.hash, key)


class UnsignedBlock(rlp.Serializable):

    fields = Block.fields[:-1]
