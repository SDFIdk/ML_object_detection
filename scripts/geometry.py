"""
Geometry module

"""

def semi_perimeter(*sides: list[float]) -> float:
    """
    Returns half the perimeter of the given sides

    """
    assert all(side >= 0 for side in sides)
    return sum(sides) / 2


def brahmagupta(a: float, b: float, c: float, d: float) -> float:
    """
    Returns the area of the cyclic quadrilateral given by the sides a, b, c, d.

    Implements Brahmagupta's formula

    References
    ----------

    *   https://en.wikipedia.org/wiki/Brahmagupta%27s_formula

    """
    s = semi_perimeter(a, b, c, d)
    return ( (s - a) * (s - b) * (s - c) * (s - d) ) ** (1 / 2)
