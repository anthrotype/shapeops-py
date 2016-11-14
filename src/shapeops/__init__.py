from __future__ import print_function, division, absolute_import
from __future__ import unicode_literals

from shapeops.shape import zsToBeziers, reduceShape, beziersToZs
from shapeops.intersections import (
    findAllSelfIntersections, findCrossIntersections, splitShape)
from shapeops.topoly import toPoly
from shapeops.rebuild import rebuildShape

import pyclipper


RESOLUTION = 1 << 17


def executeClipper(subjectPaths, clippingPaths, operation, fillRule):
    pc = pyclipper.Pyclipper()
    for p in subjectPaths:
        pc.AddPath(p, pyclipper.PT_SUBJECT)
    for p in clippingPaths:
        pc.AddPath(p, pyclipper.PT_CLIP)
    return pc.Execute(operation, fillRule, fillRule)


def removeOverlaps(shape, fillRule=pyclipper.PFT_NONZERO, resolution=RESOLUTION):
    error = 0.5 / resolution
    s1 = reduceShape(shape)
    i1 = findAllSelfIntersections(s1, shape, error)

    findCrossIntersections(s1, s1, i1, i1, True, error)

    for c in range(len(i1)):
        i1[c].sort()

    xs1 = splitShape(shape, i1, error)

    pthash = {}
    pvhash = {}

    p1 = toPoly(xs1, 1, pthash, pvhash, resolution)

    operation = pyclipper.CT_UNION
    solution_paths = executeClipper(p1, [], operation, fillRule)

    result = rebuildShape(solution_paths, [None, xs1], pthash, pvhash, resolution)
    return result


def removeOverlapsZs(zs, fillRule=pyclipper.PFT_NONZERO,
                     resolution=RESOLUTION, **kwargs):
    shape = zsToBeziers(zs)
    result = removeOverlaps(shape, fillRule=fillRule, resolution=resolution)
    return beziersToZs(result)


if __name__ == '__main__':
    import json
    import sys

    data = json.load(sys.stdin)

    result = removeOverlapsZs(data)

    print(json.dumps(result, indent=2, sort_keys=True))
