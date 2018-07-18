from plasma_core.exceptions import (
    ValidationError
)


def validate_is_integer(value, title="Value"):
    if not isinstance(value, int) or isinstance(value, bool):
        raise ValidationError(
            "{title} must be a an integer.  Got: {0}".format(type(value), title=title)
        )


def validate_gte(value, minimum, title="Value"):
    if value < minimum:
        raise ValidationError(
            "{title} {0} is not greater than or equal to {1}".format(
                value,
                minimum,
                title=title,
            )
        )
    validate_is_integer(value)


def validate_block_number(block_number, title="Block Number"):
    validate_is_integer(block_number, title="Block Number")
    validate_gte(block_number, 0, title="Block Number")


def validate_word(value, title="Value"):
    if not isinstance(value, bytes):
        raise ValidationError(
            "{title} is not a valid word. Must be of bytes type: Got: {0}".format(
                type(value),
                title=title,
            )
        )
    elif not len(value) == 32:
        raise ValidationError(
            "{title} is not a valid word. Must be 32 bytes in length: Got: {0}".format(
                len(value),
                title=title,
            )
        )
