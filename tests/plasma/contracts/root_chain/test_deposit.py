import pytest
from ethereum.tools.tester import TransactionFailed
from plasma_core.fixed_merkle import FixedMerkle
from plasma_core.transaction import Transaction


TREE_DEPTH = 10


def get_deposit_tx(owner, amount):
    """Generates a deposit transaction.

    Args:
        owner (bytes): Address of the user to own the deposit.
        amount (int): Amount to be deposited.

    Returns:
        Transaction: A transaction representing the deposit.
    """

    return Transaction(inputs=[], outputs=[(owner, amount)])


def test_deposit_should_succeed(root_chain, ethtester):
    owner, amount = ethtester.accounts[0], 100
    deposit_tx = get_deposit_tx(owner.address, amount)

    root_chain.deposit(deposit_tx.encoded, sender=owner.key, value=amount)

    merkle = FixedMerkle(TREE_DEPTH, leaves=[deposit_tx.encoded])
    plasma_block_root = root_chain.plasmaBlockRoots(1)
    assert plasma_block_root[0] == merkle.root
    assert root_chain.currentPlasmaBlockNumber() == 2


def test_deposit_invalid_value_should_fail(root_chain, ethtester):
    owner, amount = ethtester.accounts[0], 100
    deposit_tx = get_deposit_tx(owner.address, amount)

    with pytest.raises(TransactionFailed):
        root_chain.deposit(deposit_tx.encoded, sender=owner.key, value=0)


def test_deposit_invalid_outputs_should_fail(root_chain, ethtester):
    owner, amount = ethtester.accounts[0], 100
    deposit_tx = Transaction(inputs=[], outputs=[(owner.address, amount), (owner.address, amount)])

    with pytest.raises(TransactionFailed):
        root_chain.deposit(deposit_tx.encoded, sender=owner.key, value=amount)
