BLKNUM_OFFSET = 1000000000
TXINDEX_OFFSET = 10000


def decode_utxo_position(utxo_position):
    blknum = utxo_position // BLKNUM_OFFSET
    txindex = (utxo_position % BLKNUM_OFFSET) // BLKNUM_OFFSET
    oindex = utxo_position - blknum * BLKNUM_OFFSET - txindex * TXINDEX_OFFSET
    return (blknum, txindex, oindex)


def encode_utxo_position(blknum, txindex, oindex):
    return (blknum * BLKNUM_OFFSET) + (txindex * TXINDEX_OFFSET) + (oindex * 1)
