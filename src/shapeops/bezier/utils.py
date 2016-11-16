from __future__ import print_function, division, absolute_import
from __future__ import unicode_literals

from shapeops.bezier import Point
from math import sqrt, atan2, cos, sin, hypot


def align(points, line):
    tx = line.p1.x
    ty = line.p1.y
    a = -atan2(line.p2.y-ty, line.p2.x-tx)
    return [
        Point((v.x-tx)*cos(a) - (v.y-ty)*sin(a),
              (v.x-tx)*sin(a) + (v.y-ty)*cos(a))
        for v in points]


def lerp(r, v1, v2):
    return Point(
        v1.x + r*(v2.x-v1.x),
        v1.y + r*(v2.y-v1.y))


def angle(o, v1, v2):
    dx1 = v1.x - o.x
    dy1 = v1.y - o.y
    dx2 = v2.x - o.x
    dy2 = v2.y - o.y
    cross = dx1*dy2 - dy1*dx2
    m1 = sqrt(dx1*dx1 + dy1*dy1)
    m2 = sqrt(dx2*dx2 + dy2*dy2)
    dx1 /= m1
    dy1 /= m1
    dx2 /= m2
    dy2 /= m2
    dot = dx1*dx2 + dy1*dy2
    return atan2(cross, dot)


def dist(a, b):
    return hypot((b[0]-a[0]), (b[1]-a[1]))


def droots(p):
    # quadratic roots are easy
    if len(p) == 3:
        a, b, c = p[0], p[1], p[2]
        d = a - 2*b + c

        if d != 0:
            try:
                m1 = -sqrt(b*b-a*c)
            except ValueError:
                return []
            m2 = -a+b
            v1 = -(m1+m2)/d
            v2 = -(-m1+m2)/d
            return [v1, v2]
        elif b != c and d == 0:
            return [(2*b-c)/(2*(b-c))]
        return []
    # linear roots are even easier
    elif len(p) == 2:
        a, b = p
        if a != b:
            return [a/(a-b)]
        return []
    else:
        raise ValueError(len(p))


def map_(v, ds, de, ts, te):
    d1 = de-ds
    d2 = te-ts
    v2 = v-ds
    r = v2/d1
    return ts + d2*r


# Legendre-Gauss abscissae with n=24 (x_i values, defined at i=n as the roots
# of the nth order Legendre polynomial Pn(x))
Tvalues = [
    -0.0640568928626056260850430826247450385909,
     0.0640568928626056260850430826247450385909,
    -0.1911188674736163091586398207570696318404,
     0.1911188674736163091586398207570696318404,
    -0.3150426796961633743867932913198102407864,
     0.3150426796961633743867932913198102407864,
    -0.4337935076260451384870842319133497124524,
     0.4337935076260451384870842319133497124524,
    -0.5454214713888395356583756172183723700107,
     0.5454214713888395356583756172183723700107,
    -0.6480936519369755692524957869107476266696,
     0.6480936519369755692524957869107476266696,
    -0.7401241915785543642438281030999784255232,
     0.7401241915785543642438281030999784255232,
    -0.8200019859739029219539498726697452080761,
     0.8200019859739029219539498726697452080761,
    -0.8864155270044010342131543419821967550873,
     0.8864155270044010342131543419821967550873,
    -0.9382745520027327585236490017087214496548,
     0.9382745520027327585236490017087214496548,
    -0.9747285559713094981983919930081690617411,
     0.9747285559713094981983919930081690617411,
    -0.9951872199970213601799974097007368118745,
     0.9951872199970213601799974097007368118745
]

# Legendre-Gauss weights with n=24 (w_i values, defined by a function linked
# to in Pomax's Bezier primer article)
Cvalues = [
    0.1279381953467521569740561652246953718517,
    0.1279381953467521569740561652246953718517,
    0.1258374563468282961213753825111836887264,
    0.1258374563468282961213753825111836887264,
    0.1216704729278033912044631534762624256070,
    0.1216704729278033912044631534762624256070,
    0.1155056680537256013533444839067835598622,
    0.1155056680537256013533444839067835598622,
    0.1074442701159656347825773424466062227946,
    0.1074442701159656347825773424466062227946,
    0.0976186521041138882698806644642471544279,
    0.0976186521041138882698806644642471544279,
    0.0861901615319532759171852029837426671850,
    0.0861901615319532759171852029837426671850,
    0.0733464814110803057340336152531165181193,
    0.0733464814110803057340336152531165181193,
    0.0592985849154367807463677585001085845412,
    0.0592985849154367807463677585001085845412,
    0.0442774388174198061686027482113382288593,
    0.0442774388174198061686027482113382288593,
    0.0285313886289336631813078159518782864491,
    0.0285313886289336631813078159518782864491,
    0.0123412297999871995468056670700372915759,
    0.0123412297999871995468056670700372915759
]


def arcfn(t, derivativeFn):
    d = derivativeFn(t)
    return sqrt(d[0]*d[0] + d[1]*d[1])


def length(derivativeFn):
    z = 0.5
    s = 0
    for i in range(len(Tvalues)):
        t = z * Tvalues[i] + z
        s += Cvalues[i] * arcfn(t, derivativeFn)
    return z * s


def closest(LUT, point):
    mdist = 2**63
    for idx, p in enumerate(LUT):
        d = dist(point, p)
        if d < mdist:
            mdist = d
            mpos = idx
    return mdist, mpos


def pointOnLine(pt1, pt2, a, epsilon=1e-2):
    return abs(dist(pt1, a) + dist(a, pt2) - dist(pt1, pt2)) <= epsilon
