from __future__ import print_function, division, absolute_import
from __future__ import unicode_literals

from shapeops.bezier import Bezier


def lerp(a, b, t):
    return (1-t)*a + t*b


def contourZsToBeziers(contour):
    ans = []
    z0 = contour[0]
    j = 1
    while j < len(contour):
        z1 = contour[j % len(contour)]
        if z1['on']:
            seg = Bezier(
                (z0['x'], z0['y']),
                (lerp(z0['x'], z1['x'], 1 / 3),
                 lerp(z0['y'], z1['y'], 1 / 3)),
                (lerp(z0['x'], z1['x'], 2 / 3),
                 lerp(z0['y'], z1['y'], 2 / 3)),
                (z1['x'], z1['y']))
            seg._t1 = len(ans)
            seg._t2 = len(ans) + 1
            ans.append(seg)
            z0 = z1
        else:
            z2 = contour[(j + 1) % len(contour)]
            z3 = contour[(j + 2) % len(contour)]
            seg = Bezier(
                (z0['x'], z0['y']),
                (z1['x'], z1['y']),
                (z2['x'], z2['y']),
                (z3['x'], z3['y']))
            seg._t1 = len(ans)
            seg._t2 = len(ans) + 1
            ans.append(seg)
            z0 = z3
            j += 2
        j += 1
    return ans


def zsToBeziers(shape):
    return [contourZsToBeziers(c) for c in shape]


def reduceContour(contour):
    ans = []
    for j in range(len(contour)):
        seg = contour[j]
        if seg._linear:
            ans.append(seg)
            continue
        reducedSeg = seg.reduce()
        if len(reducedSeg):
            for k in range(len(reducedSeg)):
                _t1 = reducedSeg[k]._t1
                _t2 = reducedSeg[k]._t2
                reducedSeg[k]._t1 = seg._t1 + (seg._t2 - seg._t1) * _t1
                reducedSeg[k]._t2 = seg._t1 + (seg._t2 - seg._t1) * _t2
                ans.append(reducedSeg[k])
        else:
            ans.append(seg)
    return ans


def reduceShape(shape):
    return [reduceContour(c) for c in shape]


def beziersToZs(shape):
    return [contourBeziersToZs(c) for c in shape]


def onpoint(z):
    return {'x': z[0], 'y': z[1], 'on': True}


def offpoint(z):
    return {
        'x': z[0],
        'y': z[1],
        'on': False,
        'cubic': True,
    }


def contourBeziersToZs(contour):
    ans = [onpoint(contour[0].points[0])]
    for j in range(len(contour)):
        if contour[j]._linear:
            ans.append(onpoint(contour[j].points[3]))
        else:
            ans.extend([
                offpoint(contour[j].points[1]),
                offpoint(contour[j].points[2]),
                onpoint(contour[j].points[3])
            ])
    return ans
