from __future__ import print_function, division, absolute_import
from __future__ import unicode_literals
from fontTools.misc.py23 import round

import math


try:
    long
except NameError:
    long = int


def keyofz(z):
    return 'X' + repr(long(z[0])) + 'Y' + repr(long(z[1]))


def scalePoint(p, resolution):
    return round(p[0] * resolution), round(p[1] * resolution)


def toPoly(shape, sindex, pthash, pvhash, resolution):
    ans = []
    for j in range(len(shape)):
        points = []
        contour = shape[j]
        for k in range(len(contour)):
            segpts = [scalePoint(z, resolution) for z in contour[k].getLUT(
                      max(5, int(math.ceil(contour[k].length() / 5))))]
            for m in range(len(segpts)):
                # zk = keyofz(segpts[m])
                zk = segpts[m]
                isMid = m > 0 and m < len(segpts) - 1
                if isMid:
                    pthash[zk] = 0 if (zk in pthash and pthash[zk] == 0) else 1
                    if pthash[zk]:
                        pvhash[zk] = [sindex, j, k, m]
                else:
                    pthash[zk] = 0
            points.extend(segpts[1 if k > 0 else 0:])
        ans.append(points)
    return ans
