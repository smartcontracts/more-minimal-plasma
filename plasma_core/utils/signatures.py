from ethereum import utils


def sign(hash, key):
    vrs = utils.ecsign(hash, key)
    rsv = vrs[1:] + vrs[:1]
    vrs_bytes = [utils.encode_int32(i) for i in rsv[:2]] + [utils.int_to_bytes(rsv[2])]
    return b''.join(vrs_bytes)


def get_signer(hash, sig):
    v = sig[64]
    if v < 27:
        v += 27
    r = utils.bytes_to_int(sig[:32])
    s = utils.bytes_to_int(sig[32:64])
    pub = utils.ecrecover_to_pub(hash, v, r, s)
    return utils.sha3(pub)[-20:]
