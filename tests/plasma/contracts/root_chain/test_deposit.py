import pytest
from ethereum.tools.tester import TransactionFailed
from plasma_core.transaction import Transaction


def test_deposit_should_succeed(testlang):
    owner, amount = testlang.accounts[0], 100

    # Create a deposit
    testlang.deposit(owner, amount)

    # Check that the deposit was correctly created
    plasma_block = testlang.get_plasma_block(1)
    assert plasma_block.root == testlang.child_chain.get_block(1).root
    assert testlang.current_plasma_block_number == 2


def test_deposit_zero_value_should_fail(root_chain, ethtester):
    owner = ethtester.accounts[0]

    # Submitting with zero value should fail
    with pytest.raises(TransactionFailed):
        root_chain.deposit(sender=owner.key, value=0)
