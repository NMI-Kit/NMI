"""Independent sympy solutions for the grade 12 example bank (curriculum/math/grade12/examples/*units.md).

Same contract as example_solutions.py: `numbers` must appear in the example text, `facts` must all be True.
"""
import itertools
import math

import sympy as sp

x, t = sp.symbols('x t', real=True)
R = sp.Rational


def _case(numbers, facts):
    return {'numbers': [str(n) for n in numbers], 'facts': list(facts)}


def _phi(z):
    return 0.5 * (1 + math.erf(z / math.sqrt(2)))


# ----------------------------------------------------------------------------- 3 units
def e12_3_01():  # normal distribution: standard score
    z = R(510 - 500, 5)
    return _case([500, 5, 510, 490], [z == 2, round(_phi(2), 3) == 0.977, R(490 - 500, 5) == -2])


def e12_3_02():  # quadratic profit model
    P = -2 * x ** 2 + 40 * x - 150
    vertex = sp.solve(sp.diff(P, x), x)[0]
    roots = sorted(sp.solve(P, x))
    return _case(['-2x² + 40x - 150'], [vertex == 10, P.subs(x, 10) == 50, roots == [5, 15], P.subs(x, 8) > 0, P.subs(x, 3) < 0, P.subs(x, 0) == -150])


def e12_3_03():  # linear programming: check every vertex
    a, b = sp.symbols('a b', real=True)
    meet = sp.solve([2 * a + b - 100, a + b - 70], [a, b])
    vertices = [(0, 0), (50, 0), (meet[a], meet[b]), (0, 70)]
    profit = [30 * p + 20 * q for p, q in vertices]
    feasible = all(2 * p + q <= 100 and p + q <= 70 and p >= 0 and q >= 0 for p, q in vertices)
    return _case([100, 70, 30, 20], [meet == {a: 30, b: 40}, feasible, profit == [0, 1500, 1700, 1400], max(profit) == 1700, profit.index(1700) == 2])


def e12_3_04():  # a cylinder
    V = sp.pi * 3 ** 2 * 5
    lateral = 2 * sp.pi * 3 * 5
    cost = round(float(lateral) / math.pi * 3.14, 4) * 20
    return _case([3, 5, 20, '3.14'], [V == 45 * sp.pi, lateral == 30 * sp.pi, round(cost, 2) == 1884, lateral + 2 * sp.pi * 3 ** 2 == 48 * sp.pi])


def e12_3_05():  # a line through two points, an intersection, a parallel
    slope = R(10 - 2, 5 - 1)
    line = slope * (x - 1) + 2
    meet = sp.solve(sp.Eq(line, -x + 9), x)[0]
    parallel = slope * x + 4
    return _case(['A(1, 2)', 'B(5, 10)', 'y = -x + 9', '(0, 4)'],
                 [sp.expand(line) == 2 * x, meet == 3, line.subs(x, meet) == 6, parallel.subs(x, 0) == 4, sp.diff(parallel, x) == sp.diff(line, x)])


# ----------------------------------------------------------------------------- 4 units
def e12_4_01():  # a cube
    a = 4
    AG = sp.Matrix([a, a, a])
    AC = sp.Matrix([a, a, 0])
    return _case([4], [AG == sp.Matrix([a, 0, 0]) + sp.Matrix([0, a, 0]) + sp.Matrix([0, 0, a]), AG.norm() == 4 * sp.sqrt(3), AC.norm() == 4 * sp.sqrt(2), AC.norm() < AG.norm()])


def e12_4_02():  # exponential growth
    N = lambda tt: 100 * 2 ** tt
    sol = sp.solve(sp.Eq(2 ** (x + 1) + 2 ** x, 24), x)
    return _case(['100 · 2^t', '6,400', '2^(x+1) + 2^x = 24'], [N(3) == 800, N(6) == 6400, sol == [3], all(2 ** k > 0 for k in range(-5, 6))])


def e12_4_03():  # scalar product as work
    work = 3 * 4 * sp.cos(sp.pi / 3)
    mag = sp.sqrt(3 ** 2 + 4 ** 2 + 2 * work)
    return _case([3, 4, '60°'], [work == 6, mag == sp.sqrt(37), 3 * 4 * sp.cos(sp.pi / 2) == 0])


def e12_4_04():  # logarithmic equation
    sols = sp.solve(sp.Eq(x * (x - 2), 8), x)
    return _case(['log₂(x) + log₂(x - 2) = 3', 'log₂(x + y) = log₂ x + log₂ y'],
                 [sorted(sols) == [-2, 4], sp.log(4, 2) + sp.log(4 - 2, 2) == 3,
                  float(sp.log(4, 2)) == 2.0, float(sp.log(1, 2) + sp.log(3, 2)) != 2.0, -2 - 2 < 0])


def e12_4_05():  # a pyramid
    V = R(1, 3) * 36 * 4
    slant = sp.sqrt(3 ** 2 + 4 ** 2)
    lateral = 4 * R(1, 2) * 6 * slant
    return _case([6, 4, 3], [V == 48, slant == 5, lateral == 60, sp.sqrt(6 ** 2 + 4 ** 2) != slant])


def e12_4_06():  # points in space
    A, B, C = sp.Matrix([1, 2, 3]), sp.Matrix([4, 6, 3]), sp.Matrix([1, 2, 7])
    AB, AC = B - A, C - A
    return _case(['A(1, 2, 3)', 'B(4, 6, 3)', 'C(1, 2, 7)'], [AB == sp.Matrix([3, 4, 0]), AB.norm() == 5, (A + B) / 2 == sp.Matrix([R(5, 2), 4, 3]), AB.dot(AC) == 0])


def e12_4_07():  # algebraic scalar product
    a, b, c = sp.Matrix([2, 1, -2]), sp.Matrix([1, 2, 2]), sp.Matrix([1, 0, 0])
    return _case(['a = (2, 1, -2)', 'b = (1, 2, 2)', 'c = (1, 0, 0)'], [a.dot(b) == 0, a.norm() == 3, b.norm() == 3, R(a.dot(c)) / (a.norm() * c.norm()) == R(2, 3), a.dot(c) > 0])


def e12_4_08():  # the angle CAG in a cube of side 2
    A, C, G = sp.Matrix([0, 0, 0]), sp.Matrix([2, 2, 0]), sp.Matrix([2, 2, 2])
    AG, AC = G - A, C - A
    cos_angle = sp.simplify(AG.dot(AC) / (AG.norm() * AC.norm()))
    geometric = sp.atan(R(2) / AC.norm())
    return _case(['A(0, 0, 0)', 'C(2, 2, 0)', 'G(2, 2, 2)'],
                 [AG.dot(AC) == 8, sp.simplify(cos_angle - sp.sqrt(6) / 3) == 0, round(math.degrees(math.acos(float(cos_angle))), 1) == 35.3,
                  abs(float(geometric) - math.acos(float(cos_angle))) < 1e-12])


def e12_4_09():  # half-life
    M = lambda tt: 80 * R(1, 2) ** (R(tt, 5))
    return _case([80, 5, 10], [M(10) == 20, M(20) == 5, M(5) == 40, all(M(k) > 0 for k in (0, 10, 50, 100))])


def e12_4_10():  # arithmetic and geometric sequences
    a = lambda n: 3 + 4 * (n - 1)
    b = lambda n: 2 * 3 ** (n - 1)
    return _case([3, 4, 10, 2, 3], [a(10) == 39, sum(a(k) for k in range(1, 11)) == 210, b(5) == 162, sum(b(k) for k in range(1, 6)) == 242, 3 > 1])


def e12_4_11():  # x e^x
    f = x * sp.exp(x)
    d = sp.diff(f, x)
    return _case(['x · e^x'], [sp.simplify(d - (x + 1) * sp.exp(x)) == 0, sp.solve(d, x) == [-1], f.subs(x, -1) == -sp.exp(-1), d.subs(x, 0) == 1, f.subs(x, 0) == 0,
                               d.subs(x, -2) < 0, d.subs(x, 0) > 0])


def e12_4_12():  # x - ln x
    f = x - sp.log(x)
    d = sp.diff(f, x)
    tangent = f.subs(x, sp.E) + d.subs(x, sp.E) * (x - sp.E)
    return _case(['x - ln x'], [sp.solve(d, x) == [1], f.subs(x, 1) == 1, sp.diff(f, x, 2).subs(x, 1) > 0, sp.simplify(sp.expand(tangent) - (1 - 1 / sp.E) * x) == 0])


def e12_4_13():  # integrals with e^x and 1/x
    return _case(['r(t) = e^t', 'ln 3'], [sp.integrate(sp.exp(t), (t, 0, sp.log(3))) == 2, sp.integrate(1 / x, (x, 1, sp.E)) == 1,
                                          (sp.exp(0) + 2) == 3, sp.diff(sp.exp(t) + 2, t) == sp.exp(t)])


def e12_4_14():  # e^(2x) - 3e^x + 2
    f = sp.exp(2 * x) - 3 * sp.exp(x) + 2
    u = sp.symbols('u', positive=True)
    us = sorted(sp.solve(u ** 2 - 3 * u + 2, u))
    xs = [sp.log(v) for v in us]
    crit = sp.solve(sp.diff(f, x), x)
    return _case(['e^(2x) - 3e^x + 2'], [us == [1, 2], xs == [0, sp.log(2)], crit == [sp.log(R(3, 2))], sp.simplify(f.subs(x, sp.log(R(3, 2)))) == -R(1, 4),
                                          sp.exp(5) > 0])


# ----------------------------------------------------------------------------- 5 units
def e12_5_01():  # a road on a map: dividing a segment in a ratio, distance from a point to a line, parallel lines
    A, B, P = sp.Point(-4, 1), sp.Point(8, 10), sp.Point(3, 0)
    K = A + (B - A) * R(1, 3)  # AK : KB = 1 : 2
    road = sp.Line(A, B)
    a, b, c = road.coefficients
    distance = road.distance(P)
    other = road.parallel_line(P)  # the second road, through P
    between = sp.Abs(c - other.coefficients[2] * a / other.coefficients[0]) / sp.sqrt(a ** 2 + b ** 2)
    return _case(['A(-4, 1)', 'B(8, 10)', 'P(3, 0)', 'AK : KB = 1 : 2'],
                 [K == sp.Point(0, 4), A.distance(K) * 2 == K.distance(B), road.slope == R(3, 4),
                  road.contains(sp.Point(0, 4)) and road.equals(sp.Line(sp.Point(0, 4), slope=R(3, 4))),  # 3x - 4y + 16 = 0
                  distance == 5, other.contains(P), other.equals(sp.Line(sp.Point(3, 0), slope=R(3, 4))),  # 3x - 4y - 9 = 0
                  between == 5, other.distance(A) == distance])


def e12_5_02():  # exponential and logarithmic equations
    u = sp.symbols('u', positive=True)
    us = sorted(sp.solve(u ** 2 - 5 * u + 4, u))
    first = [sp.log(v, 2) for v in us]
    second = sorted(sp.solve(sp.Eq(x * (x + 6), 27), x))
    return _case(['4^x - 5·2^x + 4 = 0', 'log₃(x) + log₃(x + 6) = 3'], [us == [1, 4], first == [0, 2], second == [-9, 3], -9 < 0, 3 > 0])


def e12_5_03():  # Apollonius circle: distance to A twice the distance to B
    y = sp.symbols('y', real=True)
    eq = sp.expand(x ** 2 + y ** 2 - 4 * ((x - 3) ** 2 + y ** 2))
    circle = sp.expand((x - 4) ** 2 + y ** 2 - 4)
    A, B = sp.Point(0, 0), sp.Point(3, 0)
    return _case(['A(0, 0)', 'B(3, 0)'], [sp.simplify(eq / (-3) - circle) == 0, sp.Point(2, 0).distance(A) == 2 * sp.Point(2, 0).distance(B), sp.Point(6, 0).distance(A) == 2 * sp.Point(6, 0).distance(B),
                                          circle.subs({x: 2, y: 0}) == 0, circle.subs({x: 6, y: 0}) == 0, sp.Point(3, 0).distance(A) != 2 * sp.Point(3, 0).distance(B)])


def e12_5_04():  # ln x / x
    f = sp.log(x) / x
    d = sp.simplify(sp.diff(f, x))
    return _case(['(ln x) / x'], [sp.solve(f, x) == [1], sp.simplify(d - (1 - sp.log(x)) / x ** 2) == 0, sp.solve(sp.log(x) - 1, x) == [sp.E], f.subs(x, sp.E) == 1 / sp.E,
                                  sp.integrate(f, (x, 1, sp.E)) == R(1, 2), d.subs(x, 1) > 0, d.subs(x, 10) < 0])


def e12_5_05():  # ellipse x^2/25 + y^2/9 = 1
    a, b = 5, 3
    c = sp.sqrt(a ** 2 - b ** 2)
    P = sp.Point(3, R(12, 5))
    F1, F2 = sp.Point(4, 0), sp.Point(-4, 0)
    return _case(['x²/25 + y²/9 = 1', 'P(3, 12/5)'], [c == 4, R(9, 25) + R(12, 5) ** 2 / 9 == 1, P.distance(F1) == R(13, 5), P.distance(F2) == R(37, 5), P.distance(F1) + P.distance(F2) == 2 * a])


def e12_5_06():  # collinear points
    A, B, C = sp.Matrix([1, 1, 1]), sp.Matrix([3, 2, 3]), sp.Matrix([5, 3, 5])
    AB, AC = B - A, C - A
    return _case(['A(1, 1, 1)', 'B(3, 2, 3)', 'C(5, 3, 5)'], [AB == sp.Matrix([2, 1, 2]), AC == sp.Matrix([4, 2, 4]), AC == 2 * AB, (A + C) / 2 == B])


def e12_5_07():  # complex numbers
    z = 3 + 4 * sp.I
    w = sp.Symbol('w')  # a complex unknown
    roots = sorted(sp.solve(w ** 2 + 2 * w + 5, w), key=lambda r: sp.im(r))
    return _case(['3 + 4i', 'z² + 2z + 5 = 0'], [sp.Abs(z) == 5, sp.expand(z * sp.conjugate(z)) == 25, sp.simplify(1 / z - (R(3, 25) - R(4, 25) * sp.I)) == 0,
                                                  roots == [-1 - 2 * sp.I, -1 + 2 * sp.I], sp.conjugate(roots[0]) == roots[1]])


def e12_5_08():  # de Moivre
    value = sp.expand((1 + sp.I) ** 8)
    cube_roots = [2 * sp.exp(sp.I * sp.pi * k * 2 / 3) for k in range(3)]
    numeric = [sp.simplify(sp.expand_complex(r)) for r in cube_roots]
    return _case(['(1 + i)⁸', 'z³ = 8'], [value == 16, sp.Abs(1 + sp.I) ** 8 == 16, all(sp.simplify(r ** 3 - 8) == 0 for r in cube_roots),
                                          sp.simplify(sum(numeric)) == 0, numeric[1] == -1 + sp.sqrt(3) * sp.I, numeric[2] == -1 - sp.sqrt(3) * sp.I])


def e12_5_09():  # a right square pyramid, base 6 and height 4
    S = sp.Matrix([0, 0, 4])
    A = sp.Matrix([3, 3, 0])
    normal = sp.Matrix([4, 0, 3])  # the plane through S, (3, 3, 0) and (3, -3, 0): 4x + 3z = 12
    face_ok = all((4 * p[0] + 3 * p[2]) == 12 for p in (S, A, sp.Matrix([3, -3, 0])))
    face_angle = math.degrees(math.acos(3 / 5))
    distance = R(12) / normal.norm()
    edge_angle = math.degrees(math.atan(4 / (3 * math.sqrt(2))))
    return _case([6, 4], [face_ok, round(face_angle, 1) == 53.1, distance == R(12, 5), round(edge_angle, 1) == 43.3, edge_angle < face_angle])


SOLUTIONS = {'m' + name[1:].replace('_', '-'): fn for name, fn in globals().items()
             if name.startswith('e12_') and callable(fn)}
