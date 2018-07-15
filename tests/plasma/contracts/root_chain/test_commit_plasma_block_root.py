import pytest
from ethereum.tools.tester import TransactionFailed
from plasma_core.constants import NULL_HASH


def test_commit_plasma_block_root_should_succeed(root_chain, ethtester, ethutils):
    random_hash = ethutils.sha3('abc123')
    operator = ethtester.accounts[0]

    root_chain.commitPlasmaBlockRoot(random_hash, sender=operator.key)

    plasma_block_root = root_chain.plasmaBlockRoots(1)
    assert plasma_block_root[0] == random_hash
    assert plasma_block_root[1] == ethtester.chain.head_state.timestamp
    assert root_chain.currentPlasmaBlockNumber() == 2


def test_commit_plasma_block_root_not_operator_should_fail(root_chain, ethtester, ethutils):
    random_hash = ethutils.sha3('abc123')
    non_operator = ethtester.accounts[1]

    with pytest.raises(TransactionFailed):
        root_chain.commitPlasmaBlockRoot(random_hash, sender=non_operator.key)

    plasma_block_root = root_chain.plasmaBlockRoots(1)
    assert plasma_block_root[0] == NULL_HASH
    assert plasma_block_root[1] == 0
    assert root_chain.currentPlasmaBlockNumber() == 1
