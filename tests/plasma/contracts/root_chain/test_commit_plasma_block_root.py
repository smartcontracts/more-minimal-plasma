import pytest
from ethereum.tools.tester import TransactionFailed
from plasma_core.constants import NULL_HASH32
from plasma_core.block import Block


def test_commit_plasma_block_root_should_succeed(testlang):
    # Operator should be able to submit
    operator = testlang.accounts[0]
    block = Block()
    testlang.commit_plasma_block_root(block, signer=operator)

    # Check that the block was created correctly
    plasma_block_root = testlang.get_plasma_block(1)
    assert plasma_block_root.root == block.root
    assert plasma_block_root.timestamp == testlang.ethtester.chain.head_state.timestamp
    assert testlang.current_plasma_block_number == 2


def test_commit_plasma_block_root_not_operator_should_fail(testlang):
    # Operator should be able to submit
    non_operator = testlang.accounts[1]
    block = Block()
    with pytest.raises(TransactionFailed):
        testlang.commit_plasma_block_root(block, signer=non_operator)

    # Check nothing was submitted
    plasma_block = testlang.get_plasma_block(1)
    assert plasma_block.root == NULL_HASH32
    assert plasma_block.timestamp == 0
    assert testlang.current_plasma_block_number == 1
