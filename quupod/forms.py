"""Form utilities."""

from .utils import str2lst


def choicify(lst: [str]):
    """Make an iterable into a valid list of form choices."""
    if isinstance(lst, str):
        lst = str2lst(lst)
    return [(s, s) for s in lst]
