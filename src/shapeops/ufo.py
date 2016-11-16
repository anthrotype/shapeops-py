from __future__ import print_function, division, absolute_import
from __future__ import unicode_literals

import shapeops
from shapeops.bezier.utils import pointOnLine


class ContourDataPointPen(object):

    def __init__(self, data=None):
        self.data = data if data is not None else []
        self._points = self._closed = None

    def beginPath(self):
        assert self._points is None and self._closed is None
        self._points = []
        self._closed = True

    def endPath(self):
        points = self._points
        if len(points):
            if self._closed:
                points.append(dict(points[0]))
            self.data.append(points)
        self._points = self._closed = None

    def addPoint(self, pt, segmentType=None, smooth=False, name=None, **kwargs):
        if segmentType == "move":
            self._closed = False
        self._points.append({'x': pt[0],
                             'y': pt[1],
                             'on': False if segmentType is None else True})

    def addComponent(self, baseGlyphName, transformation):
        raise NotImplementedError


def contoursToZs(contours):
    pen = ContourDataPointPen()
    for contour in contours:
        contour.drawPoints(pen)
    return pen.data


def zsToContourPoints(points, guessSmooth=True):
    contour = []
    if not points:
        return contour
    assert points[0]['on'], 'contour must start with an on-curve point'
    closed = points[-1] == points[0]
    if closed:
        points = points[:-1]
    lastOn = points[-1]['on']
    for i, point in enumerate(points):
        x, y, on = point['x'], point['y'], point['on']
        if not closed and i == 0:
            segmentType = 'move'
        else:
            segmentType = ('curve' if (on and not lastOn) else
                           'line' if (on and lastOn) else None)
        smooth = False
        contour.append([(x, y), segmentType, smooth])
        lastOn = on
    # determine whether line/curve or curve/curve connections are "smooth"
    if guessSmooth:
        nPoints = len(contour)
        if closed:
            indices = range(-1, nPoints - 1) if nPoints > 1 else []
        else:
            indices = range(1, nPoints - 1)
        for idx in indices:
            pt, segmentType, _ = contour[idx]
            if segmentType is None:
                continue
            prevIdx, nextIdx = idx - 1, idx + 1
            if (contour[prevIdx][1] is not None and
                    contour[nextIdx][1] is not None):
                continue
            pt = contour[idx][0]
            prevPt = contour[prevIdx][0]
            nextPt = contour[nextIdx][0]
            if (pt != prevPt and pt != nextPt and prevPt != nextPt and
                    pointOnLine(prevPt, nextPt, pt)):
                contour[idx][2] = True  # set 'smooth' to True
    return contour


def drawZsWithPointPen(shape, pointPen, guessSmooth=True):
    contours = [zsToContourPoints(pts, guessSmooth) for pts in shape]
    for points in contours:
        if not points:
            continue
        pointPen.beginPath()
        for pt, segmentType, smooth in points:
            pointPen.addPoint(pt, segmentType, smooth)
        pointPen.endPath()


def union(contours, outPen, guessSmooth=True, **kwargs):
    paths = contoursToZs(contours)
    result = shapeops.union(paths, **kwargs)
    drawZsWithPointPen(result, outPen, guessSmooth=guessSmooth)


def difference(subjectContours, clippingContours, outPen, guessSmooth=True,
               **kwargs):
    subjectPaths = contoursToZs(subjectContours)
    clippingPaths = contoursToZs(clippingContours)
    result = shapeops.difference(subjectPaths, clippingPaths, **kwargs)
    drawZsWithPointPen(result, outPen, guessSmooth=guessSmooth)


def intersection(subjectContours, clippingContours, outPen, guessSmooth=True,
                 **kwargs):
    subjectPaths = contoursToZs(subjectContours)
    clippingPaths = contoursToZs(clippingContours)
    result = shapeops.intersection(subjectPaths, clippingPaths, **kwargs)
    drawZsWithPointPen(result, outPen, guessSmooth=guessSmooth)


def xor(subjectContours, clippingContours, outPen, guessSmooth=True,
        **kwargs):
    subjectPaths = contoursToZs(subjectContours)
    clippingPaths = contoursToZs(clippingContours)
    result = shapeops.xor(subjectPaths, clippingPaths, **kwargs)
    drawZsWithPointPen(result, outPen, guessSmooth=guessSmooth)


if __name__ == "__main__":
    import sys
    from defcon import Glyph
    from ufoLib.glifLib import readGlyphFromString, writeGlyphToString

    data = sys.stdin.read()

    glyph = Glyph()
    readGlyphFromString(data, glyph, glyph.getPointPen())

    contours = list(glyph)
    glyph.clearContours()
    union(contours, glyph.getPointPen())

    output = writeGlyphToString(glyph.name, glyph, glyph.drawPoints)
    sys.stdout.write(output)
