from plasma_core.utils.address import address_to_hex


NULL_BYTE = b'\x00'
NULL_ADDRESS = NULL_BYTE * 20
NULL_ADDRESS_HEX = address_to_hex(NULL_ADDRESS)
NULL_HASH = NULL_BYTE * 32
NULL_SIGNATURE = NULL_BYTE * 65
