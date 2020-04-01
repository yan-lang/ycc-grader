"""
求解最长公共子序列

ref:http://wordaligned.org/articles/longest-common-subsequence
"""

from collections import defaultdict, namedtuple
from itertools import product


def lcs_grid(xs, ys, eq):
    """Create a grid for longest common subsequence calculations.
    
    Returns a grid where grid[(j, i)] is a pair (n, move) such that
    - n is the length of the LCS of prefixes xs[:i], ys[:j]
    - move is \, ^, <, or e, depending on whether the best move
      to (j, i) was diagonal, downwards, or rightwards, or None.
    
    Example:
       T  A  R  O  T
    A 0< 1\ 1< 1< 1<
    R 0< 1^ 2\ 2< 2<
    T 1\ 1< 2^ 2< 3\
    """
    Cell = namedtuple('Cell', 'length move')
    grid = defaultdict(lambda: Cell(0, 'e'))
    sqs = product(enumerate(ys), enumerate(xs))
    for (j, y), (i, x) in sqs:
        if eq(x, y):
            cell = Cell(grid[(j - 1, i - 1)].length + 1, '\\')
        else:
            left = grid[(j, i - 1)].length
            over = grid[(j - 1, i)].length
            if left < over:
                cell = Cell(over, '^')
            else:
                cell = Cell(left, '<')
        grid[(j, i)] = cell
    return grid


def lcs(xs, ys, eq=lambda x, y: x == y):
    """Return a longest common subsequence of xs, ys."""
    # Create the LCS grid, then walk back from the bottom right corner
    grid = lcs_grid(xs, ys, eq)
    i, j = len(xs) - 1, len(ys) - 1
    lcs = list()
    for move in iter(lambda: grid[(j, i)].move, 'e'):
        if move == '\\':
            lcs.append((i, j))
            i -= 1
            j -= 1
        elif move == '^':
            j -= 1
        elif move == '<':
            i -= 1
    lcs.reverse()
    return lcs
