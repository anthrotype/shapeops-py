from __future__ import print_function, division, absolute_import
from __future__ import unicode_literals

from shapeops.bezier import Bezier
from shapeops.bezier.utils import dist


def rebuildShape(polys, recog, pthash, pvhash, resolution):
    ans = []
    for poly in polys:
        cx = rebuildContour(poly, recog, pthash, pvhash, resolution)
        if cx:
            ans.append(cx)
    return ans


def ordinalSegPts(poly, l, r, pthash, pvhash):
    if (r - l) < 2:
        return
    k = tuple(poly[l + 1])
    if k not in pvhash:
        return
    pv0 = pvhash[k]
    j = l + 2
    while j < r:
        k = tuple(poly[j])
        if k not in pvhash:
            return
        pv1 = pvhash[k]
        if pv1[0] != pv0[0] or pv1[1] != pv0[1] or pv1[2] != pv0[2]:
            return
        j += 1
    return pv0


def bezpt(p, resolution):
    x = p[0] / resolution
    y = p[1] / resolution
    return (int(x) if x.is_integer() else x,
            int(y) if y.is_integer() else y)


def rebuildContour(_poly, recog, pthash, pvhash, resolution):

    def _pthash(p):
        k = tuple(p)
        if k not in pthash:
            return None
        return pthash[k]

    j0 = 0
    while (j0 < len(_poly) and _pthash(_poly[j0])):
        j0 += 1

    poly = _poly[j0:] + _poly[:j0+1]
    j = 0
    ans = []

    while j < len(poly):
        n = j + 1
        while n < len(poly) and _pthash(poly[n]):
            n += 1
        if n < len(poly):
            pv = ordinalSegPts(poly, j, n, pthash, pvhash)
            if pv:
                seg = recog[pv[0]][pv[1]][pv[2]]
                z1 = bezpt(poly[j], resolution)
                z4 = bezpt(poly[n], resolution)
                if (dist(z1, seg.points[0]) < 1/resolution and
                        dist(z4, seg.points[3]) < 1/resolution):
                    ans.append(Bezier(z1, seg.points[1], seg.points[2], z4))
                elif (dist(z1, seg.points[3]) < 1/resolution and
                        dist(z4, seg.points[0]) < 1/resolution):
                    ans.append(Bezier(z1, seg.points[2], seg.points[1], z4))
                else:
                    t1 = seg.project(z1).t
                    t4 = seg.project(z4).t
                    if t1 < t4:
                        sseg = seg.split(t1, t4)
                        ans.append(Bezier(z1, sseg.points[1], sseg.points[2], z4))
                    elif t1 > t4:
                        sseg = seg.split(t4, t1)
                        ans.append(Bezier(z1, sseg.points[2], sseg.points[1], z4))
            else:
                m = j
                while m < n:
                    p1, p2 = poly[m], poly[m+1]
                    if (abs(p1[0] - p2[0]) >= resolution or
                            abs(p1[1] - p2[1]) >= resolution):
                        b1 = bezpt(p1, resolution)
                        b2 = bezpt(p2, resolution)
                        ans.append(Bezier(b1, b1, b2, b2))
                    m += 1
        j = n
    return ans
