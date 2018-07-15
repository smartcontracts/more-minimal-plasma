import pytest
from ethereum.tools.tester import TransactionFailed
from plasma_core.fixed_merkle import FixedMerkle
from plasma_core.transaction import Transaction
from plasma_core.utils.transactions import encode_utxo_id


TREE_DEPTH = 10


def test_start_exit_should_succeed(root_chain, ethtester, get_deposit_tx):
    owner, amount = ethtester.accounts[0], 100

    # Create a deposit
    deposit_tx = get_deposit_tx(owner.address, amount)
    root_chain.deposit(deposit_tx.encoded, sender=owner.key, value=amount)

    # Spend the deposit and submit the block
    spend_tx = Transaction(inputs=[(1, 0, 0)], outputs=[(owner.address, amount)])
    spend_tx.sign(0, owner.key)
    merkle = FixedMerkle(TREE_DEPTH, [spend_tx.encoded])
    root_chain.commitPlasmaBlockRoot(merkle.root)
    spend_tx.confirm(0, owner.key)

    # Start an exit
    utxo_position = encode_utxo_id(2, 0, 0)
    encoded_tx = spend_tx.encoded
    proof = merkle.create_membership_proof(spend_tx.encoded)
    signatures = spend_tx.full_signatures
    root_chain.startExit(utxo_position, encoded_tx, proof, signatures)

    # Check the exit was created correctly
    plasma_exit = root_chain.plasmaExit(utxo_position)
    assert plasma_exit.owner == owner.address
    assert plasma_exit.amount == amount


def test_start_exit_from_deposit_should_succeed(root_chain, ethtester, get_deposit_tx):
    owner, amount = ethtester.accounts[0], 100

    # Create a deposit
    deposit_tx = get_deposit_tx(owner.address, amount)
    root_chain.deposit(deposit_tx.encoded, sender=owner.key, value=amount)

    # Exit directly from the deposit, don't need to include signatures
    merkle = FixedMerkle(TREE_DEPTH, [deposit_tx.encoded])
    utxo_position = encode_utxo_id(1, 0, 0)
    encoded_tx = deposit_tx.encoded
    proof = merkle.create_membership_proof(deposit_tx.encoded)
    signatures = b''
    root_chain.startExit(utxo_position, encoded_tx, proof, signatures)

    # Check the exit was created correctly
    plasma_exit = root_chain.plasmaExit(utxo_position)
    assert plasma_exit.owner == owner.address
    assert plasma_exit.amount == amount


def test_start_exit_wrong_position_should_fail(root_chain, ethtester, get_deposit_tx):
    owner, amount = ethtester.accounts[0], 100

    # Create a deposit
    deposit_tx = get_deposit_tx(owner.address, amount)
    root_chain.deposit(deposit_tx.encoded, sender=owner.key, value=amount)

    # Spend the deposit and submit the block
    spend_tx = Transaction(inputs=[(1, 0, 0)], outputs=[(owner.address, amount)])
    spend_tx.sign(0, owner.key)
    merkle = FixedMerkle(TREE_DEPTH, [spend_tx.encoded])
    root_chain.commitPlasmaBlockRoot(merkle.root)

    # Start an exit
    utxo_position = encode_utxo_id(0, 0, 0)  # not the correct position
    encoded_tx = spend_tx.encoded
    proof = merkle.create_membership_proof(spend_tx.encoded)
    signatures = spend_tx.full_signatures
    with pytest.raises(TransactionFailed):
        root_chain.startExit(utxo_position, encoded_tx, proof, signatures)


def test_start_exit_wrong_tx_should_fail(root_chain, ethtester, get_deposit_tx):
    owner, amount = ethtester.accounts[0], 100

    # Create a deposit
    deposit_tx = get_deposit_tx(owner.address, amount)
    root_chain.deposit(deposit_tx.encoded, sender=owner.key, value=amount)

    # Spend the deposit and submit the block
    spend_tx = Transaction(inputs=[(1, 0, 0)], outputs=[(owner.address, amount)])
    spend_tx.sign(0, owner.key)
    merkle = FixedMerkle(TREE_DEPTH, [spend_tx.encoded])
    root_chain.commitPlasmaBlockRoot(merkle.root)
    spend_tx.confirm(0, owner.key)

    # Start an exit
    utxo_position = encode_utxo_id(2, 0, 0)
    encoded_tx = deposit_tx.encoded  # wrong transaction
    proof = merkle.create_membership_proof(spend_tx.encoded)
    signatures = spend_tx.full_signatures
    with pytest.raises(TransactionFailed):
        root_chain.startExit(utxo_position, encoded_tx, proof, signatures)


def test_start_exit_invalid_proof_should_fail(root_chain, ethtester, get_deposit_tx):
    owner, amount = ethtester.accounts[0], 100

    # Create a deposit
    deposit_tx = get_deposit_tx(owner.address, amount)
    root_chain.deposit(deposit_tx.encoded, sender=owner.key, value=amount)

    # Spend the deposit and submit the block
    spend_tx = Transaction(inputs=[(1, 0, 0)], outputs=[(owner.address, amount)])
    spend_tx.sign(0, owner.key)
    merkle = FixedMerkle(TREE_DEPTH, [spend_tx.encoded])
    root_chain.commitPlasmaBlockRoot(merkle.root)
    spend_tx.confirm(0, owner.key)

    # Start an exit
    utxo_position = encode_utxo_id(2, 0, 0)
    encoded_tx = spend_tx.encoded
    proof = b''  # use an empty proof
    signatures = spend_tx.full_signatures
    with pytest.raises(TransactionFailed):
        root_chain.startExit(utxo_position, encoded_tx, proof, signatures)


def test_start_exit_invalid_signature_should_fail(root_chain, ethtester, get_deposit_tx):
    owner, amount = ethtester.accounts[0], 100

    # Create a deposit
    deposit_tx = get_deposit_tx(owner.address, amount)
    root_chain.deposit(deposit_tx.encoded, sender=owner.key, value=amount)

    # Spend the deposit and submit the block
    spend_tx = Transaction(inputs=[(1, 0, 0)], outputs=[(owner.address, amount)])
    spend_tx.sign(0, ethtester.accounts[1].key)  # sign with the wrong account
    merkle = FixedMerkle(TREE_DEPTH, [spend_tx.encoded])
    root_chain.commitPlasmaBlockRoot(merkle.root)
    spend_tx.confirm(0, owner.key)

    # Start an exit
    utxo_position = encode_utxo_id(2, 0, 0)
    encoded_tx = spend_tx.encoded
    proof = merkle.create_membership_proof(spend_tx.encoded)
    signatures = spend_tx.full_signatures
    with pytest.raises(TransactionFailed):
        root_chain.startExit(utxo_position, encoded_tx, proof, signatures)


def test_start_exit_invalid_conf_signature_should_fail(root_chain, ethtester, get_deposit_tx):
    owner, amount = ethtester.accounts[0], 100

    # Create a deposit
    deposit_tx = get_deposit_tx(owner.address, amount)
    root_chain.deposit(deposit_tx.encoded, sender=owner.key, value=amount)

    # Spend the deposit and submit the block
    spend_tx = Transaction(inputs=[(1, 0, 0)], outputs=[(owner.address, amount)])
    spend_tx.sign(0, owner.key)
    merkle = FixedMerkle(TREE_DEPTH, [spend_tx.encoded])
    root_chain.commitPlasmaBlockRoot(merkle.root)
    spend_tx.confirm(0, ethtester.accounts[1].key)  # confirm with the wrong account

    # Start an exit
    utxo_position = encode_utxo_id(2, 0, 0)
    encoded_tx = spend_tx.encoded
    proof = merkle.create_membership_proof(spend_tx.encoded)
    signatures = spend_tx.full_signatures
    with pytest.raises(TransactionFailed):
        root_chain.startExit(utxo_position, encoded_tx, proof, signatures)
