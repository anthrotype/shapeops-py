""" Python port of the Bezier.js library by Mike 'Pomax' Kamermans. """

from __future__ import print_function, division, absolute_import
from __future__ import unicode_literals

from collections import namedtuple
from math import acos, sqrt, pi

Point = namedtuple('Point', 'x y')

from shapeops.bezier import utils


# a zero coordinate, which is surprisingly useful
ZERO = Point(0, 0)

Line = namedtuple('Line', 'p1 p2')


class Bezier(object):

    dims = ('x', 'y')

    def __init__(self, *coords):
        self.points = points = [Point(*c) for c in coords]
        self.order = len(coords) - 1

        aligned_pts = utils.align(points, Line(points[0], points[self.order]))
        for p in aligned_pts:
            if abs(p.y) > 0.0001:
                self._linear = False
                break
        else:
            self._linear = True

        self._t1 = 0
        self._t2 = 1
        self._lut = []
        self.update()

    def update(self):
        """ one-time compute derivative coordinates """
        self.dpoints = []
        p = self.points
        d = len(p)
        c = d-1
        while d > 1:
            lst = []
            for j in range(c):
                dpt = Point(
                    c * (p[j+1].x - p[j].x),
                    c * (p[j+1].y - p[j].y)
                )
                lst.append(dpt)
            self.dpoints.append(lst)
            p = lst
            d -= 1
            c -= 1

    def extrema(self):
        dims = self.dims
        result = {}
        roots = []

        for dim in dims:
            p = [getattr(v, dim) for v in self.dpoints[0]]
            result[dim] = utils.droots(p)
            if self.order == 3:
                p = [getattr(v, dim) for v in self.dpoints[1]]
                result[dim].extend(utils.droots(p))
            result[dim] = sorted(t for t in result[dim] if t >= 0 and t <= 1)
            roots.extend(result[dim])
        roots = sorted(set(roots))
        result['values'] = roots
        return result

    def hull(self, t):
        p = self.points
        q = list(p)
        # we lerp between all points at each iteration, until we have 1 point left
        while len(p) > 1:
            _p = []
            l = len(p)-1
            for i in range(l):
                pt = utils.lerp(t, p[i], p[i+1])
                q.append(pt)
                _p.append(pt)
            p = _p
        return q

    _SplitResult = namedtuple('_SplitResult', 'left right span')

    def split(self, t1, t2=None):
        # shortcuts
        if t1 == 0 and t2 is not None:
            return self.split(t2).left
        if t2 == 1:
            return self.split(t1).right

        # no shortcut: use "de Casteljau" iteration
        q = self.hull(t1)
        result = Bezier._SplitResult(
            left=(Bezier(q[0], q[3], q[5]) if self.order == 2 else
                  Bezier(q[0], q[4], q[7], q[9])),
            right=(Bezier(q[5], q[4], q[2]) if self.order == 2 else
                   Bezier(q[9], q[8], q[6], q[3])),
            span=q
        )
        # make sure we bind _t1/_t2 information!
        result.left._t1 = utils.map_(0, 0, 1, self._t1, self._t2)
        result.left._t2 = utils.map_(t1, 0, 1, self._t1, self._t2)
        result.right._t1 = utils.map_(t1, 0, 1, self._t1, self._t2)
        result.right._t2 = utils.map_(1,  0, 1, self._t1, self._t2)

        # if we have no t2, we're done
        if t2 is None:
            return result

        # if we have a t2, split again
        t2 = utils.map_(t2, t1, 1, 0, 1)
        subsplit = result.right.split(t2)
        return subsplit.left

    def derivative(self, t):
        mt = 1-t
        a = b = c = 0
        p = self.dpoints[0]
        if self.order == 2:
            p = [p[0], p[1], ZERO]
            a = mt
            b = t
        elif self.order == 3:
            a = mt*mt
            b = mt*t*2
            c = t*t
        return Point(
            a*p[0].x + b*p[1].x + c*p[2].x,
            a*p[0].y + b*p[1].y + c*p[2].y)

    def normal(self, t):
        d = self.derivative(t)
        q = sqrt(d.x*d.x + d.y*d.y)
        return Point(-d.y/q, d.x/q)

    def simple(self):
        if self.order == 3:
            points = self.points
            try:
                a1 = utils.angle(points[0], points[3], points[1])
                a2 = utils.angle(points[0], points[3], points[2])
            except ZeroDivisionError:
                return False
            else:
                if (a1 > 0 and a2 < 0) or (a1 < 0 and a2 > 0):
                    return False
        try:
            n1 = self.normal(0)
            n2 = self.normal(1)
        except ZeroDivisionError:
            return False
        else:
            s = n1[0]*n2[0] + n1[1]*n2[1]
            try:
                angle = abs(acos(s))
            except ValueError:
                return False
            else:
                return angle < pi/3

    def reduce(self):
        t1 = t2 = 0
        step = 0.01
        pass1 = []
        # first pass: split on extrema
        extrema = self.extrema()['values']
        if 0 not in extrema:
            extrema.insert(0, 0)
        if 1 not in extrema:
            extrema.append(1)

        t1 = extrema[0]
        for i in range(1, len(extrema)):
            t2 = extrema[i]
            segment = self.split(t1, t2)
            segment._t1 = t1
            segment._t2 = t2
            pass1.append(segment)
            t1 = t2

        # second pass: further reduce these segments to simple segments
        pass2 = []

        def _second_pass(p1):
            t1 = t2 = 0
            while t2 <= 1:
                t2 = t1 + step
                while t2 <= 1+step:
                    segment = p1.split(t1, t2)
                    if not segment.simple():
                        t2 -= step
                        if abs(t1 - t2) < step:
                            # we can never form a reduction
                            return
                        segment = p1.split(t1, t2)
                        segment._t1 = utils.map_(t1, 0, 1, p1._t1, p1._t2)
                        segment._t2 = utils.map_(t2, 0, 1, p1._t1, p1._t2)
                        pass2.append(segment)
                        t1 = t2
                        break
                    t2 += step

            if t1 < 1:
              segment = p1.split(t1, 1)
              segment._t1 = utils.map_(t1, 0, 1, p1._t1, p1._t2)
              segment._t2 = p1._t2
              pass2.append(segment)

        for p1 in pass1:
            _second_pass(p1)

        return pass2

    def compute(self, t):
        # shortcuts
        if t == 0:
            return self.points[0]
        elif t == 1:
            return self.points[self.order]

        p = self.points
        mt = 1-t

        # linear:
        if self.order == 1:
            return Point(
                mt*p[0].x + t*p[1].x,
                mt*p[0].y + t*p[1].y)

        # quadratic/cubic curve?
        if self.order < 4:
            mt2 = mt*mt
            t2 = t*t
            a = b = c = d = 0
            if self.order == 2:
                p = [p[0], p[1], p[2], ZERO]
                a = mt2
                b = mt*t*2
                c = t2
            elif self.order == 3:
                a = mt2*mt
                b = mt2*t*3
                c = mt*t2*3
                d = t*t2
            return Point(
                a*p[0].x + b*p[1].x + c*p[2].x + d*p[3].x,
                a*p[0].y + b*p[1].y + c*p[2].y + d*p[3].y)

        # higher order curves: use de Casteljau's computation
        dCpts = list(self.points)
        while dCpts.length > 1:
            for i in range(len(dCpts)-1):
                dCpts[i] = Point(
                    dCpts[i].x + (dCpts[i+1].x - dCpts[i].x) * t,
                    dCpts[i].y + (dCpts[i+1].y - dCpts[i].y) * t)
            dCpts.pop()
        return dCpts[0]

    get = compute

    def getLUT(self, steps=100):
        # Create lookup tables for resolving coordinate -> 't' values
        if len(self._lut) == steps:
            return self._lut
        self._lut = []
        for t in range(steps+1):
            self._lut.append(self.get(t/steps))
        return self._lut

    def length(self):
        return utils.length(self.derivative)

    _ProjectedPoint = namedtuple('Point', Point._fields+('t', 'd'))

    def project(self, point):
        # step 1: coarse check
        LUT = self.getLUT()
        l = len(LUT)-1
        mdist, mpos = utils.closest(LUT, point)
        if mpos == 0 or mpos == l:
            t = mpos/l
            pt = self.compute(t)
            return Bezier._ProjectedPoint(pt.x, pt.y, t, mdist)

        # step 2: fine check
        t1 = (mpos-1)/l
        t2 = (mpos+1)/l
        step = 0.1/l
        mdist += 1
        t = t1
        ft = t
        while t < t2+step:
            p = self.compute(t)
            d = utils.dist(point, p)
            if d < mdist:
                mdist = d
                ft = t
            t += step
        p = self.compute(ft)
        return Bezier._ProjectedPoint(p.x, p.y, ft, mdist)

    def __repr__(self):
        return "%s(%s)" % (
            self.__class__.__name__,
            ", ".join("%r" % (pt,) for pt in self.points))

    def __eq__(self, other):
        try:
            return self.points == other.points
        except AttributeError:
            return NotImplemented

    def __ne__(self, other):
        return not self.__eq__(other)
