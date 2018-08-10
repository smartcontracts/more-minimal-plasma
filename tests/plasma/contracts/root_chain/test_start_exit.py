import pytest
from ethereum.tools.tester import TransactionFailed
from plasma_core.utils.transactions import encode_utxo_position, decode_utxo_position


def test_start_exit_should_succeed(testlang):
    owner, amount = testlang.accounts[0], 100

    # Create a deposit
    deposit_blknum = testlang.deposit(owner, amount)
    deposit_utxo_position = encode_utxo_position(deposit_blknum, 0, 0)

    # Spend the deposit
    spend_utxo_position = testlang.spend_utxo(deposit_utxo_position, owner, amount, owner)
    testlang.confirm(spend_utxo_position, 0, owner)

    # Start an exit
    testlang.start_exit(owner, spend_utxo_position)

    # Check the exit was created correctly
    plasma_exit = testlang.get_plasma_exit(spend_utxo_position)
    assert plasma_exit.owner == owner.address
    assert plasma_exit.amount == amount


def test_start_exit_from_deposit_should_succeed(testlang):
    owner, amount = testlang.accounts[0], 100

    # Create a deposit
    deposit_blknum = testlang.deposit(owner, amount)
    deposit_utxo_position = encode_utxo_position(deposit_blknum, 0, 0)

    # Start an exit
    testlang.start_exit(owner, deposit_utxo_position)

    # Check the exit was created correctly
    plasma_exit = testlang.get_plasma_exit(deposit_utxo_position)
    assert plasma_exit.owner == owner.address
    assert plasma_exit.amount == amount


def test_start_exit_twice_should_fail(testlang):
    owner, amount = testlang.accounts[0], 100

    # Create a deposit
    deposit_blknum = testlang.deposit(owner, amount)
    deposit_utxo_position = encode_utxo_position(deposit_blknum, 0, 0)

    # Start an exit
    testlang.start_exit(owner, deposit_utxo_position)

    # Try to start a second exit
    with pytest.raises(TransactionFailed):
        testlang.start_exit(owner, deposit_utxo_position)


def test_start_exit_wrong_position_should_fail(testlang):
    owner, amount = testlang.accounts[0], 100

    # Create a deposit
    deposit_blknum = testlang.deposit(owner, amount)
    deposit_utxo_position = encode_utxo_position(deposit_blknum, 0, 0)

    # Spend the deposit and submit the block
    spend_utxo_position = testlang.spend_utxo(deposit_utxo_position, owner, amount, owner)
    testlang.confirm(spend_utxo_position, 0, owner)

    # Start an exit
    bond = testlang.root_chain.EXIT_BOND()
    utxo_position = encode_utxo_position(0, 0, 0)  # Using wrong utxo position
    with pytest.raises(TransactionFailed):
        testlang.root_chain.startExit(*decode_utxo_position(utxo_position),
                                      *testlang.get_exit_proof(spend_utxo_position),
                                      value=bond)


def test_start_exit_wrong_bond_value_should_fail(testlang):
    owner, amount = testlang.accounts[0], 100

    # Create a deposit
    deposit_blknum = testlang.deposit(owner, amount)
    deposit_utxo_position = encode_utxo_position(deposit_blknum, 0, 0)

    # Spend the deposit and submit the block
    spend_utxo_position = testlang.spend_utxo(deposit_utxo_position, owner, amount, owner)
    testlang.confirm(spend_utxo_position, 0, owner)

    # Start an exit
    bond = 0  # Using wrong bond value
    with pytest.raises(TransactionFailed):
        testlang.root_chain.startExit(*decode_utxo_position(spend_utxo_position),
                                      *testlang.get_exit_proof(spend_utxo_position),
                                      value=bond)


def test_start_exit_wrong_sender_should_fail(testlang):
    owner, amount = testlang.accounts[0], 100

    # Create a deposit
    deposit_blknum = testlang.deposit(owner, amount)
    deposit_utxo_position = encode_utxo_position(deposit_blknum, 0, 0)

    # Spend the deposit and submit the block
    spend_utxo_position = testlang.spend_utxo(deposit_utxo_position, owner, amount, owner)
    testlang.confirm(spend_utxo_position, 0, owner)

    # Start an exit
    bond = testlang.root_chain.EXIT_BOND()
    sender = testlang.accounts[1]  # Using wrong sender
    with pytest.raises(TransactionFailed):
        testlang.root_chain.startExit(*decode_utxo_position(spend_utxo_position),
                                      *testlang.get_exit_proof(spend_utxo_position),
                                      value=bond,
                                      sender=sender.key)


def test_start_exit_wrong_tx_should_fail(testlang):
    owner, amount = testlang.accounts[0], 100

    # Create a deposit
    deposit_blknum = testlang.deposit(owner, amount)
    deposit_utxo_position = encode_utxo_position(deposit_blknum, 0, 0)

    # Spend the deposit and submit the block
    spend_utxo_position = testlang.spend_utxo(deposit_utxo_position, owner, amount, owner)
    testlang.confirm(spend_utxo_position, 0, owner)

    # Start an exit
    bond = testlang.root_chain.EXIT_BOND()
    encoded_tx = testlang.child_chain.get_transaction(deposit_utxo_position).encoded  # Using wrong encoded tx
    (_, proof) = testlang.get_exit_proof(spend_utxo_position)
    with pytest.raises(TransactionFailed):
        testlang.root_chain.startExit(*decode_utxo_position(spend_utxo_position),
                                      encoded_tx,
                                      proof,
                                      value=bond)


def test_start_exit_invalid_proof_should_fail(testlang):
    owner, amount = testlang.accounts[0], 100

    # Create a deposit
    deposit_blknum = testlang.deposit(owner, amount)
    deposit_utxo_position = encode_utxo_position(deposit_blknum, 0, 0)

    # Spend the deposit and submit the block
    spend_utxo_position = testlang.spend_utxo(deposit_utxo_position, owner, amount, owner)
    testlang.confirm(spend_utxo_position, 0, owner)

    # Start an exit
    bond = testlang.root_chain.EXIT_BOND()
    proof = b''  # Using empty proof
    (encoded_tx, _) = testlang.get_exit_proof(spend_utxo_position)
    with pytest.raises(TransactionFailed):
        testlang.root_chain.startExit(*decode_utxo_position(spend_utxo_position),
                                      encoded_tx,
                                      proof,
                                      value=bond)
