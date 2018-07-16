import pytest
from ethereum.tools.tester import TransactionFailed
from plasma_core.constants import NULL_ADDRESS_HEX
from plasma_core.utils.transactions import encode_utxo_position


def start_exit_spend(testlang):
    owner, amount = testlang.accounts[0], 100

    # Create a deposit
    deposit_blknum = testlang.deposit(owner, amount)
    deposit_utxo_position = encode_utxo_position(deposit_blknum, 0, 0)

    # Start an exit
    testlang.start_exit(owner, deposit_utxo_position)

    # Spend the deposit
    spending_utxo_position = testlang.spend_utxo(deposit_utxo_position, owner, amount, owner)
    testlang.confirm(spending_utxo_position, 0, owner)

    return (deposit_utxo_position, spending_utxo_position)


def test_challenge_exit_should_succeed(testlang):
    owner, amount = testlang.accounts[0], 100

    # Create a deposit
    deposit_blknum = testlang.deposit(owner, amount)
    deposit_utxo_position = encode_utxo_position(deposit_blknum, 0, 0)

    # Start an exit
    testlang.start_exit(owner, deposit_utxo_position)

    # Check that the exit was created
    plasma_exit = testlang.get_plasma_exit(deposit_utxo_position)
    assert plasma_exit.owner == owner.address
    assert plasma_exit.amount == amount

    # Spend the deposit
    spending_utxo_position = testlang.spend_utxo(deposit_utxo_position, owner, amount, owner)
    testlang.confirm(spending_utxo_position, 0, owner)

    # Challenge the exit
    testlang.challenge_exit(deposit_utxo_position, spending_utxo_position)

    # Check that the exit was removed
    plasma_exit = testlang.get_plasma_exit(deposit_utxo_position)
    assert plasma_exit.owner == NULL_ADDRESS_HEX  # address is removed
    assert plasma_exit.amount == amount  # amount is not removed


def test_challenge_exit_invalid_tx_should_fail(testlang):
    (exiting_utxo_position, spending_utxo_position) = start_exit_spend(testlang)

    # Exit should fail
    encoded_tx = testlang.child_chain.get_transaction(exiting_utxo_position).encoded  # Using the wrong tx
    (_, confirmation_signature) = testlang.get_challenge_proof(exiting_utxo_position, spending_utxo_position)
    with pytest.raises(TransactionFailed):
        testlang.root_chain.challengeExit(exiting_utxo_position,
                                          encoded_tx,
                                          confirmation_signature)


def test_challenge_exit_invalid_confirmation_signatures_should_fail(testlang):
    (exiting_utxo_position, spending_utxo_position) = start_exit_spend(testlang)

    # Exit should fail
    confirmation_signature = b''  # Using empty confirmation signatures
    (encoded_tx, _) = testlang.get_challenge_proof(exiting_utxo_position, spending_utxo_position)
    with pytest.raises(TransactionFailed):
        testlang.root_chain.challengeExit(exiting_utxo_position,
                                          encoded_tx,
                                          confirmation_signature)
