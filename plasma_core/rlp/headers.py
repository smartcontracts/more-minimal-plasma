import time
from typing import (
    overload
)

import rlp
from rlp.sedes import (
    big_endian_int
)

from plasma_core.constants import (
    NULL_HASH32
)

from eth_typing import (
    Hash32
)

from eth_hash.auto import keccak

from eth.utils.hexadecimal import (
    encode_hex,
)

from .sedes import (
    merkle_root
)


class BlockHeader(rlp.Serializable):
    fields = [
        ('state_root', merkle_root),
        ('transaction_root', merkle_root),
        ('block_number', big_endian_int),
        ('timestamp', big_endian_int),
    ]

    @overload
    def __init__(self,
                 block_number: int,
                 timestamp: int=None,
                 state_root: Hash32=NULL_HASH32,
                 transaction_root: Hash32=NULL_HASH32) -> None:
        ...

    def __init__(self,  # noqa: F811
                 block_number,
                 timestamp=None,
                 state_root=NULL_HASH32,
                 transaction_root=NULL_HASH32):
        if timestamp is None:
            timestamp = int(time.time())
        super().__init__(
            state_root=state_root,
            transaction_root=transaction_root,
            block_number=block_number,
            timestamp=timestamp
        )

    def __repr__(self) -> str:
        return '<BlockHeader #{0} {1}>'.format(
            self.block_number,
            encode_hex(self.hash)[2:10]
        )

    _hash = None

    @property
    def hash(self) -> Hash32:
        if self._hash is None:
            self._hash = keccak(rlp.encode(self))
