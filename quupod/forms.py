"""Form utilities."""


def choicify(lst):
    """Make an iterable into a valid list of form choices."""
    return [(s, s) for s in lst]
