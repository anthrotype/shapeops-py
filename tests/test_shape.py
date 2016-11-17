from __future__ import print_function, division, absolute_import
from __future__ import unicode_literals

from shapeops.shape import (
    contourZsToBeziers, zsToBeziers, reduceContour, reduceShape,
    contourBeziersToZs, beziersToZs)
from shapeops.bezier import Bezier

import pytest


BASIC_SHAPE_ZS = [
    [{'on': True, 'x': 72, 'y': 56},
     {'on': True, 'x': 218, 'y': 56},
     {'on': True, 'x': 218, 'y': 202},
     {'on': True, 'x': 72, 'y': 202},
     {'on': True, 'x': 72, 'y': 56}],
    [{'on': True, 'x': 163, 'y': 217},
     {'on': False, 'x': 163, 'y': 176},
     {'on': False, 'x': 196, 'y': 143},
     {'on': True, 'x': 237, 'y': 143},
     {'on': False, 'x': 278, 'y': 143},
     {'on': False, 'x': 311, 'y': 176},
     {'on': True, 'x': 311, 'y': 217},
     {'on': False, 'x': 311, 'y': 258},
     {'on': False, 'x': 278, 'y': 291},
     {'on': True, 'x': 237, 'y': 291},
     {'on': False, 'x': 196, 'y': 291},
     {'on': False, 'x': 163, 'y': 258},
     {'on': True, 'x': 163, 'y': 217}]
]


BASIC_SHAPE_BEZIERS = [
   [Bezier((72, 56),
           (120.66666666666666, 56.0),
           (169.33333333333331, 56.0),
           (218, 56)),
    Bezier((218, 56),
           (218.0, 104.66666666666666),
           (218.0, 153.33333333333331),
           (218, 202)),
    Bezier((218, 202),
           (169.33333333333334, 202.0),
           (120.66666666666667, 202.0),
           (72, 202)),
    Bezier((72, 202),
           (72.0, 153.33333333333334),
           (72.0, 104.66666666666667),
           (72, 56))],
   [Bezier((163, 217), (163, 176), (196, 143), (237, 143)),
    Bezier((237, 143), (278, 143), (311, 176), (311, 217)),
    Bezier((311, 217), (311, 258), (278, 291), (237, 291)),
    Bezier((237, 291), (196, 291), (163, 258), (163, 217))]
]


def test_contourZsToBeziers():
    rect = contourZsToBeziers(BASIC_SHAPE_ZS[0])
    circle = contourZsToBeziers(BASIC_SHAPE_ZS[1])

    assert len(rect) == 4
    assert len(circle) == 4

    assert all(isinstance(seg, Bezier) for seg in rect)
    assert all(isinstance(seg, Bezier) for seg in circle)

    assert rect[0].points[0] == (72, 56)
    assert rect[0].points[1] == pytest.approx((120.6667, 56))
    assert rect[0].points[2] == pytest.approx((169.3333, 56))
    assert rect[0].points[-1] == (218, 56)

    assert circle[0].points[0] == (163, 217)
    assert circle[0].points[1] == (163, 176)
    assert circle[0].points[2] == (196, 143)
    assert circle[0].points[-1] == (237, 143)

    assert rect[0]._t1 == 0
    assert rect[0]._t2 == 1
    assert rect[-1]._t1 == 3
    assert rect[-1]._t2 == 4

    assert circle[1]._t1 == 1
    assert circle[1]._t2 == 2
    assert circle[2]._t1 == 2
    assert circle[2]._t2 == 3


def test_zsToBeziers():
    shape = zsToBeziers(BASIC_SHAPE_ZS)
    assert len(shape) == 2


def test_reduceContour():
    rect, circle = zsToBeziers(BASIC_SHAPE_ZS)

    rerect = reduceContour(rect)

    assert rect == rerect
    assert all(seg._linear for seg in rerect)

    recircle = reduceContour(circle)

    assert len(circle) == 4
    assert len(recircle) == 8
    assert not any(seg._linear for seg in recircle)

    redux = [Bezier((274, 281), (263, 287), (251, 291), (237, 291)),
             Bezier((237, 291), (237, 281)),
             Bezier((237, 281), (274, 281))]

    reredux = reduceContour(redux)

    assert redux == reredux


def test_reduceShape():
    reshape = reduceShape(zsToBeziers(BASIC_SHAPE_ZS))
    assert len(reshape) == 2


def test_contourBeziersToZs():
    rect, circle = BASIC_SHAPE_BEZIERS

    zrect = contourBeziersToZs(rect)
    zcircle = contourBeziersToZs(circle)

    assert len(zrect) == len(rect) + 1
    assert len(zcircle) == len(circle)*3 + 1

    assert zrect[0] == zrect[-1]
    assert zcircle[0] == zcircle[-1]

    assert all(p['on'] for p in zrect)
    assert len([p for p in zcircle if not p['on']]) == 2*len(circle)
    assert all([p['cubic'] for p in zcircle if not p['on']])


def test_beziersToZs():
    shape = beziersToZs(BASIC_SHAPE_BEZIERS)
    assert len(shape) == 2
    assert all(isinstance(p, dict) for contour in shape for p in contour)
