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
    glyph = Glyph()
    pen = glyph.getPointPen()
    for contour in BASIC_CONTOURS:
        pen.beginPath()
        for pt, segmentType, smooth in contour:
            pen.addPoint(pt, segmentType, smooth)
        pen.endPath()
    return glyph


def test_contoursToZs(basic_glyph):
    assert contoursToZs(basic_glyph) == BASIC_Z_SHAPE


def test_contoursToZs_open_contour():
    glyph = Glyph()
    pen = glyph.getPointPen()
    pen.beginPath()
    pen.addPoint((0, 0), 'move')
    pen.addPoint((1, 1), 'line')
    pen.addPoint((2, 2), 'line')
    pen.endPath()

    shape = contoursToZs(glyph)

    assert shape == [[{'x': 0, 'y': 0, 'on': True},
                      {'x': 1, 'y': 1, 'on': True},
                      {'x': 2, 'y': 2, 'on': True}]]


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


def test_zsToContourPoints_smooth_duplicate_points():
    pts = [{'x': 0, 'y': 0, 'on': True},
           {'x': 5, 'y': 5, 'on': False},
           {'x': 10, 'y': 10, 'on': False},
           {'x': 15, 'y': 10, 'on': True},
           {'x': 15, 'y': 10, 'on': True},  # duplicate point
           {'x': 20, 'y': 10, 'on': False},
           {'x': 25, 'y': 5, 'on': False},
           {'x': 30, 'y': 0, 'on': True},
           {'x': 0, 'y': 0, 'on': True}]
    contour = zsToContourPoints(pts, guessSmooth=True)

    assert all(pt[2] is False for pt in contour)  # no smooth


def test_zsToContourPoints_open_shape():
    pts = [{'x': 0, 'y': 0, 'on': True},
           {'x': 1, 'y': 1, 'on': True},
           {'x': 2, 'y': 2, 'on': True}]

    assert zsToContourPoints(pts) == [[(0, 0), 'move', False],
                                      [(1, 1), 'line', False],
                                      [(2, 2), 'line', False]]


@pytest.mark.parametrize("guessSmooth", [True, False])
def test_drawZsWithPointPen(guessSmooth):
    glyph = Glyph()
    pen = glyph.getPointPen()
    assert len(glyph) == 0

    drawZsWithPointPen(BASIC_Z_SHAPE, pen, guessSmooth=guessSmooth)

    assert len(glyph) == 2
    assert glyph[0][0].smooth is False
    assert glyph[1][0].smooth is guessSmooth
