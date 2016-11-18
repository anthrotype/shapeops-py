from __future__ import print_function, division, absolute_import
from __future__ import unicode_literals
from collections import namedtuple

try:
    from itertools import izip as zip
except ImportError:
    pass

from shapeops.bezier.utils import dist
from shapeops.py23 import isclose
import math


def bez3bbox(x0, y0, x1, y1, x2, y2, x3, y3):
    tvalues = []
    for i in range(2):
        if i == 0:
            b = 6 * x0 - 12 * x1 + 6 * x2
            a = -3 * x0 + 9 * x1 - 9 * x2 + 3 * x3
            c = 3 * x1 - 3 * x0
        else:
            b = 6 * y0 - 12 * y1 + 6 * y2
            a = -3 * y0 + 9 * y1 - 9 * y2 + 3 * y3
            c = 3 * y1 - 3 * y0
        if abs(a) < 1e-12:
            if abs(b) < 1e-12:
                continue
            t = -c / b
            if 0 < t and t < 1:
                tvalues.append(t)
            continue
        b2ac = b * b - 4 * c * a
        if b2ac < 0:
            continue
        sqrtb2ac = math.sqrt(b2ac)
        t1 = (-b + sqrtb2ac) / (2 * a)
        if 0 < t1 and t1 < 1:
            tvalues.append(t1)
        t2 = (-b - sqrtb2ac) / (2 * a)
        if 0 < t2 and t2 < 1:
            tvalues.append(t2)

    xvalues = [None]*len(tvalues)
    yvalues = [None]*len(tvalues)
    j = len(tvalues)-1
    while j >= 0:
        t = tvalues[j]
        mt = 1 - t
        xvalues[j] = (mt * mt * mt * x0) + (3 * mt * mt * t * x1) + (3 * mt * t * t * x2) + (t * t * t * x3)
        yvalues[j] = (mt * mt * mt * y0) + (3 * mt * mt * t * y1) + (3 * mt * t * t * y2) + (t * t * t * y3)
        j -= 1

    xvalues.extend([x0, x3])
    yvalues.extend([y0, y3])

    xmin = min(v for v in xvalues)
    ymin = min(v for v in yvalues)
    xmax = max(v for v in xvalues)
    ymax = max(v for v in yvalues)

    return (
        {'mid': (xmax + xmin) / 2, 'size': xmax - xmin},
        {'mid': (ymax + ymin) / 2, 'size': ymax - ymin}
    )


def bboxof(c):
    if hasattr(c, '__caryll_bbox'):
        return c.__caryll_bbox
    else:
        c.__caryll_bbox = bez3bbox(
            c.points[0][0], c.points[0][1],
            c.points[1][0], c.points[1][1],
            c.points[2][0], c.points[2][1],
            c.points[3][0], c.points[3][1]
        )
        return c.__caryll_bbox


def bboxOverlap(b1, b2):
    l = b1[0]['mid']
    t = b2[0]['mid']
    d = (b1[0]['size'] + b2[0]['size']) / 2
    if abs(l - t) >= d:
        return False

    l = b1[1]['mid']
    t = b2[1]['mid']
    d = (b1[1]['size'] + b2[1]['size']) / 2
    if abs(l - t) >= d:
        return False

    return True


def pairIteration(c1, c2, curveIntersectionThreshold=0.5, results=None):
    if results is None:
        results = []
    c1b = bboxof(c1)
    c2b = bboxof(c2)
    threshold = curveIntersectionThreshold
    if ((c1b[0]['size'] + c1b[1]['size']) < threshold and
            (c2b[0]['size'] + c2b[1]['size']) < threshold):
        results.append(
            [(c1._t1 + c1._t2) / 2,
             (c2._t1 + c2._t2) / 2])
        return results

    cc1 = c1.split(0.5)
    cc2 = c2.split(0.5)

    cb1l = bboxof(cc1.left)
    cb1r = bboxof(cc1.right)
    cb2l = bboxof(cc2.left)
    cb2r = bboxof(cc2.right)

    if bboxOverlap(cb1l, cb2l):
        pairIteration(cc1.left, cc2.left, threshold, results)
    if bboxOverlap(cb1r, cb2l):
        pairIteration(cc1.right, cc2.left, threshold, results)
    if bboxOverlap(cb1l, cb2r):
        pairIteration(cc1.left, cc2.right, threshold, results)
    if bboxOverlap(cb1r, cb2r):
        pairIteration(cc1.right, cc2.right, threshold, results)
    return results


_Pair = namedtuple('_Pair', ['left', 'right'])


def curveOverlap(c1, c2):
    return (all(isclose(a, b)
                for p1, p2 in zip(c1.points, c2.points)
                for a, b in zip(p1, p2)) or
            all(isclose(a, b)
                for p1, p2 in zip(c1.points, reversed(c2.points))
                for a, b in zip(p1, p2)))


def curveIntersects(c1, c2, curveIntersectionThreshold):
    pairs = []
    # step 1: pair off any overlapping segments
    b1 = []
    b2 = []
    for j in range(len(c1)):
        b1.append(bboxof(c1[j]))
    for j in range(len(c2)):
        b2.append(bboxof(c2[j]))
    for j in range(len(c1)):
        for k in range(len(c2)):
            if bboxOverlap(b1[j], b2[k]) and not curveOverlap(c1[j], c2[k]):
                pairs.append(_Pair(c1[j], c2[k]))

    # step 2: for each pairing, run through the convergence algorithm
    intersections = []
    for pair in pairs:
        result = pairIteration(
            pair.left, pair.right, curveIntersectionThreshold, [])
        if len(result) > 0:
            intersections.extend(result)

    return intersections


def findAllSelfIntersections(shape, origshape, ERROR):
    ans = []
    for c in range(len(shape)):
        contour = shape[c]
        length = len(contour) - 2
        results = []
        # For any close contour, neighbour segments should not have any intersection
        for i in range(length):
            left = contour[i:i+1]
            right = contour[i+2:]
            result = curveIntersects(left, right, ERROR)
            results.extend(result)
        for j in range(len(origshape[c])+1):
            results.append([j])
        ans.append(
            [item for sublist in results for item in sublist]
        )
    return ans


def findCrossIntersections(shape1, shape2, i1, i2, notsame, ERROR):
    for c in range(len(shape1)):
        for d in range(len(shape2)):
            if not notsame or c < d:
                l = shape1[c]
                r = shape2[d]
                intersections = curveIntersects(l, r, ERROR)
                i1[c].extend(x[0] for x in intersections)
                i2[d].extend(x[1] for x in intersections)


def splitShape(shape, irecs, ERROR):
    ans = []
    for j in range(len(shape)):
        ans.append(splitContour(shape[j], irecs[j], ERROR))
    return ans


def splitContour(contour, irec, ERROR):
    z0 = contour[0].get(0)
    jc = 0
    tlast = 0
    ans = []

    for j in range(len(irec)):
        t = irec[j] - jc
        pt = contour[jc].get(t)
        if t >= 1 or dist(pt, z0) >= ERROR * 2:
            ans.append(contour[jc].split(tlast, t))
            z0 = pt
            if t < 1:
                tlast = t
            else:
                tlast = 0
                jc += 1
        else:
            if tlast >= 1:
                tlast = 0
                jc += 1

    return ans
