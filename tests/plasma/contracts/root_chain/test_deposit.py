import pytest
from ethereum.tools.tester import TransactionFailed
from plasma_core.fixed_merkle import FixedMerkle
from plasma_core.transaction import Transaction


TREE_DEPTH = 10


def test_deposit_should_succeed(root_chain, ethtester, get_deposit_tx):
    owner, amount = ethtester.accounts[0], 100

    # Create a deposit
    deposit_tx = get_deposit_tx(owner.address, amount)
    root_chain.deposit(deposit_tx.encoded, sender=owner.key, value=amount)

    # Check that the deposit was correctly created
    merkle = FixedMerkle(TREE_DEPTH, leaves=[deposit_tx.encoded])
    plasma_block_root = root_chain.plasmaBlockRoots(1)
    assert plasma_block_root[0] == merkle.root
    assert root_chain.currentPlasmaBlockNumber() == 2


def test_deposit_invalid_value_should_fail(root_chain, ethtester, get_deposit_tx):
    owner, amount = ethtester.accounts[0], 100

    # Submitting with a mismatched value should throw
    deposit_tx = get_deposit_tx(owner.address, amount)
    with pytest.raises(TransactionFailed):
        root_chain.deposit(deposit_tx.encoded, sender=owner.key, value=0)


def test_deposit_invalid_outputs_should_fail(root_chain, ethtester):
    owner, amount = ethtester.accounts[0], 100

    # Submitting with more than one output should throw
    deposit_tx = Transaction(inputs=[], outputs=[(owner.address, amount), (owner.address, amount)])
    with pytest.raises(TransactionFailed):
        root_chain.deposit(deposit_tx.encoded, sender=owner.key, value=amount)
