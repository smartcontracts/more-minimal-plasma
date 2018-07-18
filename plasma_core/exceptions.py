class PlasmaError(Exception):
    """
    Base class for all Plasma errors.
    """
    pass


class NonexistentMemberException(PlasmaError):
    """
    Raised when a specified leaf is not in a Merkle tree.
    """
    pass


class TxAlreadySpentException(PlasmaError):
    """
    Raised when a transaction is already spent.
    """
    pass


class InvalidTxSignatureException(PlasmaError):
    """
    Raised when a transaction signature is invalid.
    """
    pass


class InvalidBlockSignatureException(PlasmaError):
    """
    Raised when a block signature is invalid.
    """
    pass


class TxAmountMismatchException(PlasmaError):
    """
    Raised when input amounts are less than output amounts.
    """
    pass


class InvalidBlockMerkleException(PlasmaError):
    """
    Raised when a block tree is invalid.
    """
    pass


class ValidationError(PlasmaError):
    """
    Raised when something does not pass a validation check.
    """
    pass


class HeaderNotFound(PlasmaError):
    """
    Raised when a header for a specific block number is not found.
    """
    pass


class CanonicalHeadNotFound(PlasmaError):
    """
    Raised when no canonical head is set for the chain.
    """
    pass


class TransactionNotFound(PlasmaError):
    """
    Raised when a transaction cannot be found in the chain.
    """
    pass
