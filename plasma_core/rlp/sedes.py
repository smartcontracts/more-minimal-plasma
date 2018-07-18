from rlp.sedes import (
    Binary,
)

merkle_root = Binary.fixed_length(32, allow_empty=True)
