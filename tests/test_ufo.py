from __future__ import print_function, division, absolute_import
from __future__ import unicode_literals

from defcon import Glyph

from shapeops.ufo import contoursToZs, zsToContourPoints, drawZsWithPointPen

import pytest


BASIC_CONTOURS = [
    [[(72, 56), 'line', False],
     [(218, 56), 'line', False],
     [(218, 202), 'line', False],
     [(72, 202), 'line', False]],
    [[(163, 217), 'curve', True],
     [(163, 176), None, False],
     [(196, 143), None, False],
     [(237, 143), 'curve', True],
     [(278, 143), None, False],
     [(311, 176), None, False],
     [(311, 217), 'curve', True],
     [(311, 258), None, False],
     [(278, 291), None, False],
     [(237, 291), 'curve', True],
     [(196, 291), None, False],
     [(163, 258), None, False]],
]


BASIC_Z_SHAPE = [
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


@pytest.fixture
def basic_glyph():
    g = Glyph()
    pen = g.getPointPen()
    for contour in BASIC_CONTOURS:
        pen.beginPath()
        for pt, segmentType, smooth in contour:
            pen.addPoint(pt, segmentType, smooth)
        pen.endPath()
    return g


def test_contoursToZs(basic_glyph):
    assert contoursToZs(basic_glyph) == BASIC_Z_SHAPE


def test_zsToContourPoints_smooth():
    contours = [zsToContourPoints(pts, guessSmooth=True)
                for pts in BASIC_Z_SHAPE]

    assert contours == BASIC_CONTOURS


def test_zsToContourPoints_no_smooth():
    contours = [zsToContourPoints(pts, guessSmooth=False)
                for pts in BASIC_Z_SHAPE]
    expected = [[[pt, segmentType, False]
                 for pt, segmentType, _ in contour]
                for contour in BASIC_CONTOURS]

    assert contours != BASIC_CONTOURS
    assert contours == expected


def test_drawZsWithPointPen():
    glyph = Glyph()
    pen = glyph.getPointPen()

    assert len(glyph) == 0

    drawZsWithPointPen(BASIC_Z_SHAPE, pen, guessSmooth=True)

    assert len(glyph) == 2
    assert glyph[0][0].smooth is False
    assert glyph[1][0].smooth is True

    glyph.clearContours()

    assert len(glyph) == 0

    drawZsWithPointPen(BASIC_Z_SHAPE, pen, guessSmooth=False)

    assert len(glyph) == 2
    assert glyph[1][0].smooth is False
