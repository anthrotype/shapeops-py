from __future__ import print_function, division, absolute_import
from __future__ import unicode_literals

import unittest

from shapeops.py23 import isclose


NAN = float('nan')
INF = float('inf')
NINF = float('-inf')


class IsCloseTests(unittest.TestCase):
    """
    Tests taken from Python 3.5 test_math.py:
    https://hg.python.org/cpython/file/v3.5.2/Lib/test/test_math.py
    """
    isclose = staticmethod(isclose)

    def assertIsClose(self, a, b, *args, **kwargs):
        self.assertTrue(self.isclose(a, b, *args, **kwargs),
                        msg="%s and %s should be close!" % (a, b))

    def assertIsNotClose(self, a, b, *args, **kwargs):
        self.assertFalse(self.isclose(a, b, *args, **kwargs),
                         msg="%s and %s should not be close!" % (a, b))

    def assertAllClose(self, examples, *args, **kwargs):
        for a, b in examples:
            self.assertIsClose(a, b, *args, **kwargs)

    def assertAllNotClose(self, examples, *args, **kwargs):
        for a, b in examples:
            self.assertIsNotClose(a, b, *args, **kwargs)

    def test_negative_tolerances(self):
        # ValueError should be raised if either tolerance is less than zero
        with self.assertRaises(ValueError):
            self.assertIsClose(1, 1, rel_tol=-1e-100)
        with self.assertRaises(ValueError):
            self.assertIsClose(1, 1, rel_tol=1e-100, abs_tol=-1e10)

    def test_identical(self):
        # identical values must test as close
        identical_examples = [(2.0, 2.0),
                              (0.1e200, 0.1e200),
                              (1.123e-300, 1.123e-300),
                              (12345, 12345.0),
                              (0.0, -0.0),
                              (345678, 345678)]
        self.assertAllClose(identical_examples, rel_tol=0.0, abs_tol=0.0)

    def test_eight_decimal_places(self):
        # examples that are close to 1e-8, but not 1e-9
        eight_decimal_places_examples = [(1e8, 1e8 + 1),
                                         (-1e-8, -1.000000009e-8),
                                         (1.12345678, 1.12345679)]
        self.assertAllClose(eight_decimal_places_examples, rel_tol=1e-8)
        self.assertAllNotClose(eight_decimal_places_examples, rel_tol=1e-9)

    def test_near_zero(self):
        # values close to zero
        near_zero_examples = [(1e-9, 0.0),
                              (-1e-9, 0.0),
                              (-1e-150, 0.0)]
        # these should not be close to any rel_tol
        self.assertAllNotClose(near_zero_examples, rel_tol=0.9)
        # these should be close to abs_tol=1e-8
        self.assertAllClose(near_zero_examples, abs_tol=1e-8)

    def test_identical_infinite(self):
        # these are close regardless of tolerance -- i.e. they are equal
        self.assertIsClose(INF, INF)
        self.assertIsClose(INF, INF, abs_tol=0.0)
        self.assertIsClose(NINF, NINF)
        self.assertIsClose(NINF, NINF, abs_tol=0.0)

    def test_inf_ninf_nan(self):
        # these should never be close (following IEEE 754 rules for equality)
        not_close_examples = [(NAN, NAN),
                              (NAN, 1e-100),
                              (1e-100, NAN),
                              (INF, NAN),
                              (NAN, INF),
                              (INF, NINF),
                              (INF, 1.0),
                              (1.0, INF),
                              (INF, 1e308),
                              (1e308, INF)]
        # use largest reasonable tolerance
        self.assertAllNotClose(not_close_examples, abs_tol=0.999999999999999)

    def test_zero_tolerance(self):
        # test with zero tolerance
        zero_tolerance_close_examples = [(1.0, 1.0),
                                         (-3.4, -3.4),
                                         (-1e-300, -1e-300)]
        self.assertAllClose(zero_tolerance_close_examples, rel_tol=0.0)

        zero_tolerance_not_close_examples = [(1.0, 1.000000000000001),
                                             (0.99999999999999, 1.0),
                                             (1.0e200, .999999999999999e200)]
        self.assertAllNotClose(zero_tolerance_not_close_examples, rel_tol=0.0)

    def test_assymetry(self):
        # test the assymetry example from PEP 485
        self.assertAllClose([(9, 10), (10, 9)], rel_tol=0.1)

    def test_integers(self):
        # test with integer values
        integer_examples = [(100000001, 100000000),
                            (123456789, 123456788)]

        self.assertAllClose(integer_examples, rel_tol=1e-8)
        self.assertAllNotClose(integer_examples, rel_tol=1e-9)

    # XXX Not supported yet
    #
    # def test_decimals(self):
    #     # test with Decimal values
    #     from decimal import Decimal

    #     decimal_examples = [(Decimal('1.00000001'), Decimal('1.0')),
    #                         (Decimal('1.00000001e-20'), Decimal('1.0e-20')),
    #                         (Decimal('1.00000001e-100'), Decimal('1.0e-100'))]
    #     self.assertAllClose(decimal_examples, rel_tol=1e-8)
    #     self.assertAllNotClose(decimal_examples, rel_tol=1e-9)

    def test_fractions(self):
        # test with Fraction values
        from fractions import Fraction

        # could use some more examples here!
        fraction_examples = [(Fraction(1, 100000000) + 1, Fraction(1))]
        self.assertAllClose(fraction_examples, rel_tol=1e-8)
        self.assertAllNotClose(fraction_examples, rel_tol=1e-9)
