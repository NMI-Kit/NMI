"""Independent sympy solutions for the grade 11 example bank (curriculum/math/grade11/examples/*units.md).

Same contract as example_solutions.py: `numbers` must appear in the example text, `facts` must all be True.
"""
import math

import sympy as sp

x, t = sp.symbols('x t', real=True)
R = sp.Rational


def _case(numbers, facts):
    return {'numbers': [str(n) for n in numbers], 'facts': list(facts)}


def _mean_sd(values):
    n = len(values)
    mean = R(sum(values), n)
    var = sum((v - mean) ** 2 for v in values) / n
    return mean, sp.sqrt(var)


def _phi(z):  # the standard normal distribution function
    return 0.5 * (1 + math.erf(z / math.sqrt(2)))


# ----------------------------------------------------------------------------- 3 units
def e11_3_01():  # compound growth, not 3 x 10%
    after3 = 2000 * R(11, 10) ** 3
    return _case(['2,000', '10%', '2,600', '30%'],
                 [2000 * R(11, 10) == 2200, after3 == 2662, 2000 * (1 + 3 * R(1, 10)) == 2600, after3 != 2600, after3 == int(after3)])


def e11_3_02():  # same mean, different spread
    a, b = [70, 70, 90, 90], [78, 78, 82, 82]
    (ma, sa), (mb, sb) = _mean_sd(a), _mean_sd(b)
    return _case(['70، 70، 90، 90', '78، 78، 82، 82'], [ma == 80, mb == 80, sa == 10, sb == 2, sb < sa])


def e11_3_03():  # two draws without replacement
    both_red = R(6, 10) * R(5, 9)
    different = R(6, 10) * R(4, 9) + R(4, 10) * R(6, 9)
    return _case([10, 6, 4, '0.36'], [both_red == R(1, 3), different == R(8, 15), R(6, 10) ** 2 == R(9, 25), both_red != R(6, 10) ** 2])


def e11_3_04():  # scale: lengths by k, areas by k squared
    k = 50000
    km = 6 * k / sp.Integer(100) / 1000
    area_km2 = 4 * sp.Integer(k) ** 2 / 10 ** 4 / 10 ** 6  # cm^2 -> m^2 -> km^2
    return _case(['1:50,000', 6, 4, '200,000'], [km == 3, area_km2 == 1, 4 * k == 200000, 4 * k != 4 * k ** 2])


def e11_3_05():  # similar triangles
    k = R(12, 8)
    area_abc = R(8 * 10, 2)
    height_def = 10 * k
    area_def = R(12, 1) * height_def / 2
    return _case([8, 12, 30, 10, 40, 60],
                 [k == R(3, 2), 30 * k == 45, height_def == 15, area_abc == 40, area_def == 90, area_def == 40 * k ** 2, 40 * k == 60, area_def != 60])


def e11_3_06():  # isosceles roof, a parallel line
    b = (180 - 40) / 2
    return _case([40], [b == 70, 70 == b, 180 - 70 == 110])


def e11_3_07():  # trapezoid, the midline does not halve the area
    area = R(12 + 8, 2) * 5
    mid = R(12 + 8, 2)
    upper = R(8 + mid, 2) * R(5, 2)
    lower = R(mid + 12, 2) * R(5, 2)
    return _case([12, 8, 5, 40], [area == 50, area * 40 == 2000, mid == 10, upper == R(45, 2), lower == R(55, 2), upper + lower == area, upper != lower])


def e11_3_08():  # ladder 10 m reaching 8 m
    base = sp.sqrt(10 ** 2 - 8 ** 2)
    angle = math.degrees(math.asin(0.8))
    return _case([10, 8, 60], [base == 6, round(angle, 1) == 53.1, angle < 60, 10 * sp.cos(sp.pi / 3) == 5])


def e11_3_09():  # compound interest and a car losing value
    saving = 10000 * R(11, 10) ** 2
    car = 50000 * R(8, 10) ** 2
    return _case(['10,000', '50,000', '10%', '20%'], [saving == 12100, car == 32000, 50000 * R(8, 10) ** 5 == R(16384), 50000 * R(8, 10) ** 5 > 0])


def e11_3_10():  # standard deviation of the wages of two branches
    (m1, s1), (m2, s2) = _mean_sd([5000, 5000, 7000, 7000]), _mean_sd([6000] * 4)
    return _case(['5,000', '7,000', '6,000'], [m1 == 6000, s1 == 1000, m2 == 6000, s2 == 0])


def e11_3_11():  # +10% then -10% is not the same price
    up = 200 * R(11, 10)
    down = up * R(9, 10)
    return _case([200, '10%'], [up == 220, down == 198, down != 200])


# ----------------------------------------------------------------------------- 4 units
def e11_4_01():  # conditional probability and independence
    girl_sport, boy_sport = 45, 20
    p_girl_given_sport = R(girl_sport, girl_sport + boy_sport)
    p_sport_given_girl = R(girl_sport, 60)
    independent = R(60, 100) * R(girl_sport + boy_sport, 100) == R(girl_sport, 100)
    return _case([100, 60, 40, 45, 20], [p_girl_given_sport == R(9, 13), p_sport_given_girl == R(3, 4), not independent, R(60, 100) * R(65, 100) == R(39, 100)])


def e11_4_02():  # 1 / (x^2 - 4)
    f = 1 / (x ** 2 - 4)
    return _case(['1 / (x² - 4)'],
                 [sorted(sp.solve(x ** 2 - 4, x)) == [-2, 2], sp.limit(f, x, sp.oo) == 0, sp.limit(f, x, 2, '+') == sp.oo, sp.limit(f, x, 2, '-') == -sp.oo,
                  f.subs(x, 3) > 0, f.subs(x, 0) < 0, f.subs(x, -3) > 0, sp.simplify(f.subs(x, -x) - f) == 0])


def e11_4_03():  # statistics of 8 values, and a shift of 2
    data = [2, 4, 4, 4, 5, 5, 7, 9]
    mean, sd = _mean_sd(data)
    shifted = [v + 2 for v in data]
    return _case(['2، 4، 4، 4، 5، 5، 7، 9'],
                 [mean == 5, R(data[3] + data[4], 2) == R(9, 2), max(set(data), key=data.count) == 4, sd == 2, _mean_sd(shifted) == (7, 2)])


def e11_4_04():  # normal distribution
    z85, z60 = (85 - 70) / 10, (60 - 70) / 10
    between = _phi(1) - _phi(-1)
    return _case([70, 10, 85, 60, 80, 90],
                 [z85 == 1.5, z60 == -1.0, round(between, 2) == 0.68, (90 - 80) / 10 == 1.0, z85 > 1.0])


def e11_4_05():  # a rectangle of area 4, the least perimeter
    P = 2 * x + 8 / x
    zeros = sp.solve(sp.diff(P, x), x)
    positive = [z for z in zeros if z > 0]
    return _case([4], [positive == [2], P.subs(x, 2) == 8, sp.diff(P, x, 2).subs(x, 2) > 0, sp.diff(P, x).subs(x, 1) < 0, sp.diff(P, x).subs(x, 3) > 0,
                       4 / sp.Integer(2) == 2])


def e11_4_06():  # linear regression of 5 points
    xs, ys = [1, 2, 3, 4, 5], [55, 60, 70, 75, 90]
    mx, my = R(sum(xs), 5), R(sum(ys), 5)
    sxy = sum((a - mx) * (b - my) for a, b in zip(xs, ys))
    sxx = sum((a - mx) ** 2 for a in xs)
    a = sxy / sxx
    b = my - a * mx
    return _case(['(1, 55)', '(5, 90)', 6, 10, '129.5'], [a == R(17, 2), b == R(89, 2), a * 6 + b == R(191, 2), a * 10 + b == R(259, 2), a * 10 + b > 100])


def e11_4_07():  # grouped marks: mean, median, probability
    counts = {60: 2, 70: 6, 80: 8, 90: 4}
    n = sum(counts.values())
    values = sorted(v for v, c in counts.items() for _ in range(c))
    mean = R(sum(v * c for v, c in counts.items()), n)
    median = R(values[9] + values[10], 2)
    at_least_80 = R(counts[80] + counts[90], n)
    return _case([20, 60, 70, 80, 90], [n == 20, mean == 77, median == 80, median > mean, at_least_80 == R(3, 5), R(counts[90], counts[80] + counts[90]) == R(1, 3)])


def e11_4_08():  # sqrt(2x + 1)
    f = sp.sqrt(2 * x + 1)
    d = sp.diff(f, x)
    tangent = f.subs(x, 4) + d.subs(x, 4) * (x - 4)
    return _case(['√(2x + 1)', 4],
                 [f.subs(x, 4) == 3, d.subs(x, 4) == R(1, 3), sp.expand(tangent) == x / 3 + R(5, 3), sp.solve_univariate_inequality(2 * x + 1 >= 0, x, relational=False) == sp.Interval(-R(1, 2), sp.oo),
                  sp.simplify(d - 1 / sp.sqrt(2 * x + 1)) == 0, d.subs(x, 0) > 0])


def e11_4_09():  # circle (x-3)^2 + (y-4)^2 = 25
    y = sp.symbols('y', real=True)
    circle = (x - 3) ** 2 + (y - 4) ** 2 - 25
    on_axis = sorted(sp.solve(circle.subs(y, 0), x))
    tangent_points = sp.solve(circle.subs(y, 9), x)
    above = sp.solve(circle.subs(y, 10), x)
    return _case([3, 4, 5, 'y = 9'], [circle.subs({x: 0, y: 0}) == 0, on_axis == [0, 6], on_axis[1] - on_axis[0] == 6, tangent_points == [3], above == []])


def e11_4_10():  # circle theorems
    return _case([50, 80, 110], [2 * 50 == 100, 180 - 80 == 100, 80 + 110 != 180])


def e11_4_11():  # sine rule, the ambiguous case
    b = 5 * sp.sin(sp.pi / 4) / sp.sin(sp.pi / 6)
    sin_b = R(8) * R(1, 2) / 5
    b1 = math.degrees(math.asin(0.8))
    b2 = 180 - b1
    return _case([30, 5, 45, 8], [sp.simplify(b - 5 * sp.sqrt(2)) == 0, 180 - 30 - 45 == 105, sin_b == R(4, 5), round(b1, 1) == 53.1, round(b2, 1) == 126.9, 30 + b2 < 180])


def e11_4_12():  # integrals: distance, a definite integral, the area
    s = sp.integrate(2 * t + 1, (t, 0, t))
    g = x ** 2 - 4
    integral = sp.integrate(g, (x, 0, 3))
    area = sp.integrate(-g, (x, 0, 2)) + sp.integrate(g, (x, 2, 3))
    return _case(['2t + 1', 'x² - 4', 4, 3], [sp.expand(s) == t ** 2 + t, s.subs(t, 4) == 20, integral == -3, area == R(23, 3), area != integral])


def e11_4_13():  # tangent to a circle at a point
    y = sp.symbols('y', real=True)
    on_circle = (4 - 1) ** 2 + (6 - 2) ** 2 == 25
    radius_slope = R(6 - 2, 4 - 1)
    tangent = -1 / radius_slope * (x - 4) + 6
    return _case(['(x - 1)² + (y - 2)² = 25', 'P(4, 6)'],
                 [on_circle, radius_slope == R(4, 3), sp.expand(3 * x + 4 * tangent - 36) == 0, tangent.subs(x, 12) == 0, tangent.subs(x, 0) == 9, radius_slope * (-1 / radius_slope) == -1])


def e11_4_14():  # chord, area and angle in a circle of radius 10
    A, B = sp.Point(6, 8), sp.Point(-6, 8)
    O = sp.Point(0, 0)
    cos_angle = (200 - A.distance(B) ** 2) / 200
    return _case(['O(0, 0)', 'A(6, 8)', 'B(-6, 8)', 10],
                 [A.distance(O) == 10, B.distance(O) == 10, A.distance(B) == 12, R(1, 2) * 12 * 8 == 48, cos_angle == R(7, 25), round(math.degrees(math.acos(cos_angle)), 1) == 73.7])


def e11_4_15():  # a line and a parabola
    sols = sorted(sp.solve(sp.Eq(x ** 2 - 6 * x + 8, x - 2), x))
    pts = [(v, v - 2) for v in sols]
    disc = (-7) ** 2 - 4 * 1 * 28
    return _case(['y = x - 2', 'y = x² - 6x + 8', 'y = x - 20'],
                 [sols == [2, 5], pts == [(2, 0), (5, 3)], sp.sqrt((5 - 2) ** 2 + (3 - 0) ** 2) == 3 * sp.sqrt(2), disc < 0])


# ----------------------------------------------------------------------------- 5 units
def e11_5_01():  # tide: h(t) = 2 + 2 sin(pi t / 6)
    h = 2 + 2 * sp.sin(sp.pi * t / 6)
    at = lambda v: sp.simplify(h.subs(t, v))
    return _case(['2 + 2·sin(πt / 6)', 1],
                 [at(3) == 4, at(9) == 0, at(7) == 1, at(11) == 1, at(0) == 2, at(6) == 2, at(12) == 2, at(9) == 0])


def e11_5_02():  # V(t) = t^3 - 6t^2 + 9t + 1
    V = t ** 3 - 6 * t ** 2 + 9 * t + 1
    v2 = sp.diff(V, t, 2)
    return _case(['t³ - 6t² + 9t + 1'],
                 [sp.solve(v2, t) == [2], V.subs(t, 2) == 3, v2.subs(t, 1) < 0, v2.subs(t, 3) > 0, min(V.subs(t, k) for k in range(0, 5)) >= 0,
                  sp.diff(x ** 4, x, 2).subs(x, 0) == 0, sp.diff(x ** 4, x, 2).subs(x, 1) > 0, sp.diff(x ** 4, x, 2).subs(x, -1) > 0])


def e11_5_03():  # a bouncing ball: geometric sequence
    a1, q = 48, R(1, 2)
    a4 = a1 * q ** 3
    s4 = a1 * (1 - q ** 4) / (1 - q)
    s_inf = a1 / (1 - q)
    return _case([48, 24, 12], [a4 == 6, s4 == 90, s_inf == 96, abs(2) >= 1])


def e11_5_04():  # fence on three sides
    A = x * (40 - 2 * x)
    crit = sp.solve(sp.diff(A, x), x)
    return _case([40], [sp.expand(A) == -2 * x ** 2 + 40 * x, crit == [10], A.subs(x, 10) == 200, sp.diff(A, x, 2) == -4, 0 < 10 < 20, A.subs(x, 0) == 0, A.subs(x, 20) == 0])


def e11_5_05():  # induction: sum of odd numbers; n^2 + n + 41
    k = sp.symbols('k', integer=True, positive=True)
    step = sp.simplify(k ** 2 + (2 * k + 1) - (k + 1) ** 2)
    primes = all(sp.isprime(n * n + n + 41) for n in range(1, 40))
    return _case([1, 39, 41], [step == 0, 1 == 1 ** 2, primes, not sp.isprime(40 * 40 + 40 + 41), 40 * 40 + 40 + 41 == 41 ** 2])


def e11_5_06():  # wave height 10 + sin t + cos t
    h = 10 + sp.sin(t) + sp.cos(t)
    d = sp.diff(h, t)
    return _case(['10 + sin t + cos t'],
                 [sp.simplify(d - (sp.cos(t) - sp.sin(t))) == 0, sp.simplify(d.subs(t, sp.pi / 4)) == 0, sp.simplify(h.subs(t, sp.pi / 4) - (10 + sp.sqrt(2))) == 0,
                  h.subs(t, 0) == 11, h.subs(t, sp.pi) == 9, sp.diff(sp.sin(3 * t), t) == 3 * sp.cos(3 * t)])


def e11_5_07():  # Bernoulli: five true/false questions
    p = R(1, 2)
    exactly3 = sp.binomial(5, 3) * p ** 5
    at_least4 = (sp.binomial(5, 4) + sp.binomial(5, 5)) * p ** 5
    return _case([5, '1/2'], [exactly3 == R(5, 16), at_least4 == R(3, 16), p ** 5 / at_least4 == R(1, 6), sp.binomial(5, 3) == 10])


def e11_5_08():  # integration: position from the speed, areas
    s = sp.integrate(3 * t ** 2 + 2, t)
    C = sp.solve(sp.Eq(s.subs(t, 1) + sp.Symbol('C'), 5), sp.Symbol('C'))[0]
    position = s + C
    area = sp.integrate(4 - x ** 2, (x, -2, 2))
    return _case(['3t² + 2', 's(1) = 5', '4 - x²'],
                 [sp.expand(position) == t ** 3 + 2 * t + 2, position.subs(t, 0) == 2, sp.integrate(sp.cos(x), (x, 0, sp.pi / 2)) == 1, area == R(32, 3),
                  sorted(sp.solve(4 - x ** 2, x)) == [-2, 2]])


def e11_5_09():  # arithmetic sequence of savings
    a = lambda n: 5 + 3 * (n - 1)
    S = lambda n: sum(a(k) for k in range(1, n + 1))
    first = min(n for n in range(1, 100) if S(n) >= 500)
    return _case([5, 3, 10, 500, 17], [a(10) == 32, S(10) == 185, first == 18, S(17) == 493, S(18) == 549])


SOLUTIONS = {'m' + name[1:].replace('_', '-'): fn for name, fn in globals().items()
             if name.startswith('e11_') and callable(fn)}
