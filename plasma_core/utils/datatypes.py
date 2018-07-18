from cytoolz import (
    assoc,
    groupby
)

from eth_utils import (
    to_dict,
    to_set
)

from typing import (
    Any,
    Dict,
    Tuple,
    Iterator,
    List
)


def _is_local_prop(prop: str) -> bool:
    return len(prop.split('.')) == 1


def _extract_top_level_key(prop: str) -> str:
    left, _, _ = prop.partition('.')
    return left


def _extract_tail_key(prop: str) -> str:
    _, _, right = prop.partition('.')
    return right


@to_dict
def _get_local_overrides(overrides: Dict[str, Any]) -> Iterator[Tuple[str, Any]]:
    for prop, value in overrides.items():
        if _is_local_prop(prop):
            yield prop, value


@to_dict
def _get_sub_overrides(overrides: Dict[str, Any]) -> Iterator[Tuple[str, Any]]:
    