from __future__ import print_function, division, absolute_import
from __future__ import unicode_literals

from ufoLib.pointPen import BasePointToSegmentPen, GuessSmoothPointPen

from shapeops.bezier import Bezier
from shapeops.shape import lerp
import shapeops


class BezierDataPointPen(BasePointToSegmentPen):

    def __init__(self):
        super(BezierDataPointPen, self).__init__()
        self.contours = []

    def _flushContour(self, segments):
        if not segments:
            return
        closed = segments[0][0] != "move"
        if closed:
            # the BasePointToSegmentPen.endPath method that calls _flushContour
            # rotates the point list of closed contours so that they end with
            # the first on-curve point. We restore the original starting point.
            segments = segments[-1:] + segments[:-1]
        contour = []
        prev_points = segments[-1][1]
        prev_on_curve = prev_points[-1][0]
        for segment_type, points in segments:
            if segment_type == "move":
                pass
            elif segment_type == "curve":
                segment = Bezier(prev_on_curve, *(p[0] for p in points))
                segment._t1 = len(contour)
                segment._t2 = len(contour) + 1
                contour.append(segment)
            elif segment_type == "line":
                on_curve = points[-1][0]
                segment = Bezier(
                    prev_on_curve,
                    (lerp(prev_on_curve[0], on_curve[0], 1/3),
                     lerp(prev_on_curve[1], on_curve[1], 1/3)),
                    (lerp(prev_on_curve[0], on_curve[0], 2/3),
                     lerp(prev_on_curve[1], on_curve[1], 2/3)),
                    on_curve)
                segment._t1 = len(contour)
                segment._t2 = len(contour) + 1
                contour.append(segment)
            else:
                raise AssertionError(segment_type)
            prev_on_curve = points[-1][0]
        self.contours.append(contour)

    def addComponent(self, baseGlyphName, transformation):
        raise NotImplementedError


class BezierContour(object):

    def __init__(self, beziers):
        segments = []
        for bezier in beziers:
            if bezier._linear:
                segment_type = "line"
                points = bezier.points[-1:]
            else:
                segment_type = "curve"
                points = bezier.points[1:]
            segments.append((segment_type, points))
        self.segments = segments

    def drawPoints(self, pen):
        pen.beginPath()
        last_offcurves = []
        for i, (segment_type, points) in enumerate(self.segments):
            if segment_type in ("move", "line"):
                assert len(points) == 1, (
                    "illegal line segment point count: %d" % len(points))
                pt = points[0]
                pen.addPoint(pt, segment_type)
            elif segment_type == "curve":
                assert len(points) >= 3, (
                    "illegal curve segment point count: %d" % len(points))
                offcurves = points[:-1]
                if offcurves:
                    if i == 0:
                        # any off-curve points preceding the first on-curve
                        # will be appended at the end of the contour
                        last_offcurves = offcurves
                    else:
                        for pt in offcurves:
                            pen.addPoint(pt, None)
                pt = points[-1]
                pen.addPoint(pt, segment_type)
            else:
                raise AssertionError(
                    "unexpected segment type: %r" % segment_type)
        for pt in last_offcurves:
            pen.addPoint(pt, None)
        pen.endPath()


def contoursToBeziers(shape):
    pen = BezierDataPointPen()
    for contour in shape:
        contour.drawPoints(pen)
    return pen.contours


def beziersToContours(shape):
    return [BezierContour(beziers) for beziers in shape]


def removeOverlaps(contours, outPen, guessSmooth=True, **kwargs):
    shape = contoursToBeziers(contours)
    result = shapeops.removeOverlaps(shape, **kwargs)
    if guessSmooth:
        outPen = GuessSmoothPointPen(outPen)
    for contour in beziersToContours(result):
        contour.drawPoints(outPen)


if __name__ == "__main__":
    import sys
    from defcon import Glyph
    from ufoLib.glifLib import readGlyphFromString, writeGlyphToString

    data = sys.stdin.read()

    glyph = Glyph()
    readGlyphFromString(data, glyph, glyph.getPointPen())

    contours = list(glyph)
    glyph.clearContours()
    removeOverlaps(contours, glyph.getPointPen())

    output = writeGlyphToString(glyph.name, glyph, glyph.drawPoints)
    print(output)
