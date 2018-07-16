from plasma_core.constants import WEEKS, NULL_ADDRESS_HEX
from plasma_core.utils.transactions import encode_utxo_position


def test_process_exits_should_succeed(testlang):
    owner, amount = testlang.accounts[0], 100

    # Create a deposit
    deposit_blknum = testlang.deposit(owner, amount)
    deposit_utxo_position = encode_utxo_position(deposit_blknum, 0, 0)

    # Start an exit
    testlang.start_exit(owner, deposit_utxo_position)

    # Move forward in time
    testlang.forward_timestamp(2 * WEEKS)

    # Process exits
    testlang.process_exits()

    # Check that the exit was processed
    plasma_exit = testlang.get_plasma_exit(deposit_utxo_position)
    assert plasma_exit.owner == NULL_ADDRESS_HEX  # owner should be deleted
    assert plasma_exit.amount == amount  # amount should be unchanged
