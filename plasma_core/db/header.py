from abc import ABC, abstractmethod
import functools
from typing import Tuple, Iterable

import rlp

from eth_utils import (
    encode_hex,
)

from eth_typing import (
    Hash32,
    BlockNumber,
)

from plasma_core.exceptions import (
    HeaderNotFound,
    CanonicalHeadNotFound
)
from plasma_core.db.backends.base import BaseDB
from plasma_core.db.schema import SchemaV1
from plasma_core.rlp.headers import BlockHeader
from plasma_core.validation import (
    validate_block_number,
    validate_word,
)


class BaseHeaderDB(ABC):
    db = None  # type: BaseDB

    def __init__(self, db: BaseDB) -> None:
        self.db = db

    #
    # Canonical Chain API
    #
    @abstractmethod
    def get_canonical_block_hash(self, block_number: BlockNumber) -> Hash32:
        raise NotImplementedError("ChainDB classes must implement this method")

    @abstractmethod
    def get_canonical_block_header_by_number(self, block_number: BlockNumber) -> BlockHeader:
        raise NotImplementedError("ChainDB classes must implement this method")

    @abstractmethod
    def get_canonical_head(self) -> BlockHeader:
        raise NotImplementedError("ChainDB classes must implement this method")

    #
    # Header API
    #
    @abstractmethod
    def get_block_header_by_hash(self, block_hash: Hash32) -> BlockHeader:
        raise NotImplementedError("ChainDB classes must implement this method")

    @abstractmethod
    def header_exists(self, block_hash: Hash32) -> bool:
        raise NotImplementedError("ChainDB classes must implement this method")


class HeaderDB(BaseHeaderDB):
    #
    # Canonical Chain API
    #
    def get_canonical_block_hash(self, block_number: BlockNumber) -> Hash32:
        validate_block_number(block_number, title="Block Number")
        number_to_hash_key = SchemaV1.make_block_number_to_hash_lookup_key(block_number)
    
        try:
            encoded_key = self.db[number_to_hash_key]
        except KeyError:
            raise HeaderNotFound(
                "No canonical header for block number #{0}".format(block_number)
            )
        else:
            return rlp.decode(encoded_key, sedes=rlp.sedes.binary)

    def get_canonical_block_header_by_number(self, block_number: BlockNumber) -> BlockHeader:
        validate_block_number(block_number, title="Block Number")
        return self.get_block_header_by_hash(self.get_canonical_block_hash(block_number))

    def get_canonical_head(self) -> BlockHeader:
        try:
            canonical_head_hash = self.db[SchemaV1.make_canonical_head_hash_lookup_key()]
        except KeyError:
            raise CanonicalHeadNotFound("No canonical head set for this chain")
        return self.get_block_header_by_hash(canonical_head_hash)

    #
    # Header API
    #
    def get_block_header_by_hash(self, block_hash: Hash32) -> BlockHeader:
        validate_word(block_hash, title="Block Hash")
        try:
            header_rlp = self.db[block_hash]
        except KeyError:
            raise HeaderNotFound("No header with hash {0} found".format(
                encode_hex(block_hash)))
        return _decode_block_header(header_rlp)

    def header_exists(self, block_hash: Hash32) -> bool:
        validate_word(block_hash, title="Block Hash")
        return block_hash in self.db


@functools.lru_cache(128)
def _decode_block_header(header_rlp: bytes) -> BlockHeader:
    return rlp.decode(header_rlp, sedes=BlockHeader)
