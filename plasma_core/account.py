class EthereumAccount(object):
    """Represents an Ethereum account.

    Attributes:
        address (int): The account's public address.
        key (bytes): The account's private key.
    """

    def __init__(self, address, key):
        self.address = address
        self.key = key
