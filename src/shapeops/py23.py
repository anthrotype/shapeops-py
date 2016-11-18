from __future__ import print_function, division, absolute_import
from __future__ import unicode_literals

import math


def _isclose(a, b, rel_tol=1e-09, abs_tol=0):
    """
    Python 2 implementation of Python 3.5 math.isclose()
    https://hg.python.org/cpython/file/v3.5.2/Modules/mathmodule.c#l1993
    """
    # sanity check on the inputs
    if rel_tol < 0 or abs_tol < 0:
        raise ValueError("tolerances must be non-negative")
    # short circuit exact equality -- needed to catch two infinities of
    # the same sign. And perhaps speeds things up a bit sometimes.
    if a == b:
        return True
    # This catches the case of two infinities of opposite sign, or
    # one infinity and one finite number. Two infinities of opposite
    # sign would otherwise have an infinite relative tolerance.
    # Two infinities of the same sign are caught by the equality check
    # above.
    if math.isinf(a) or math.isinf(b):
        return False
    # now do the regular computation
    # this is essentially the "weak" test from the Boost library
    diff = math.fabs(b - a)
    result = ((diff <= math.fabs(rel_tol * a)) or
              (diff <= math.fabs(rel_tol * b)) or
              (diff <= abs_tol))
    return result


try:
    isclose = math.isclose
except AttributeError:
    isclose = _isclose
