"""Independent sympy solutions for the example bank (curriculum/math/grade10/examples/*units.md).

Each function recomputes one example from the numbers in its story. `numbers` are the story numbers
that must appear in the example's text; `facts` must all be True (the answers come out clean, the trap
the "علّل" section points at is a real mistake). tests/offline/test_kit.py checks both, so a wrong
number cannot reach the kit.
"""
import sympy as sp

x, t = sp.symbols('x t', real=True)
R = sp.Rational
S = sp.S


def _case(numbers, facts):
    return {'numbers': [str(n) for n in numbers], 'facts': list(facts)}


# ----------------------------------------------------------------------------- 3 units
def e10_3_01():  # reading a table: share, pie angle, share after a new group joins
    total = 45 + 30 + 15 + 30
    share = R(30, total)
    angle = R(45, total) * 360
    after = R(45, total + 10)
    return _case([45, 30, 15, 30, 120, 10],
                 [total == 120, share == R(1, 4), angle == 135, after < R(45, total), float(after) < 0.375])


def e10_3_02():  # frequency table: relative frequency, "8 or more", the mode is the most frequent value
    counts = {5: 2, 6: 3, 7: 6, 8: 5, 9: 3, 10: 1}
    n = sum(counts.values())
    return _case([20, 2, 3, 6, 5, 3, 1],
                 [n == 20, R(counts[7], n) == R(3, 10), R(counts[8] + counts[9] + counts[10], n) == R(9, 20),
                  max(counts, key=counts.get) == 7, max(counts) == 10])


def e10_3_03():  # mean, median, mode, weighted mean
    pay = [4000, 4200, 4200, 4600, 7000]
    mean = R(sum(pay), len(pay))
    median = sorted(pay)[2]
    weighted = R(5 * 4800 + 3 * 3600, 8)
    plain = R(4800 + 3600, 2)
    return _case(['4,000', '4,200', '4,600', '7,000', '4,800', '3,600'],
                 [mean == 4800, median == 4200, max(set(pay), key=pay.count) == 4200, weighted == 4350,
                  plain == 4200, weighted != plain])


def e10_3_04():  # complement, ordered pairs with replacement
    red, blue, green = 5, 4, 3
    total = red + blue + green
    pairs = total ** 2
    p_red_blue = R(red * blue, pairs)
    return _case([12, 5, 4, 3],
                 [total == 12, R(red, total) == R(5, 12), 1 - R(green, total) == R(3, 4), pairs == 144,
                  p_red_blue == R(5, 36), p_red_blue == R(blue * red, pairs)])


def e10_3_05():  # grouped goals: mean, median, tail probability, "at least two"
    goals = {0: 4, 1: 5, 2: 6, 3: 3, 4: 2}
    n = sum(goals.values())
    values = sorted(g for g, c in goals.items() for _ in range(c))
    mean = R(sum(g * c for g, c in goals.items()), n)
    median = R(values[9] + values[10], 2)
    return _case([20, 4, 5, 6, 3, 2],
                 [n == 20, mean == R(17, 10), median == 2, R(goals[3] + goals[4], n) == R(1, 4),
                  R(goals[2] + goals[3] + goals[4], n) == R(11, 20), R(11, 20) > R(1, 2)])


def e10_3_06():  # composite perimeter with a semicircle
    semi = sp.pi * 10
    whole = 30 + 30 + 20 + semi
    cost = (80 + R(314, 10)) * 25
    return _case([30, 20, 25, '3.14', 'طول قوس نصف الدائرة'],
                 [sp.simplify(semi - 10 * sp.pi) == 0, sp.simplify(whole - (80 + 10 * sp.pi)) == 0,
                  cost == R(2785), R(314, 10) == 10 * R(314, 100)])


def e10_3_07():  # average speed is total distance over total time, not the mean of the speeds
    go, back = R(6, 12), R(6, 8)
    avg = R(12) / (go + back)
    return _case([6, 12, 8],
                 [go * 60 == 30, back * 60 == 45, avg == R(48, 5), avg != R(12 + 8, 2)])


def e10_3_08():  # right triangle area, hypotenuse, grass cost, wrong base-times-side area
    hyp = sp.sqrt(12 ** 2 + 16 ** 2)
    area = R(12 * 16, 2)
    return _case([12, 16, 35],
                 [hyp == 20, area == 96, area * 35 == 3360, R(20 * 12, 2) == 120, R(20 * 12, 2) != area])


def e10_3_09():  # tiles: count, cost with spare tiles, halving the side quadruples the count
    area = 6 * 4
    tiles = R(area) / R(1, 2) ** 2
    small = R(area) / R(1, 4) ** 2
    return _case([6, 4, 50, 18, 5, 25],
                 [area == 24, tiles == 96, (tiles + 5) * 18 == 1818, small == 384, small == 4 * tiles])


def e10_3_10():  # a field and a runner; doubling the sides doubles the perimeter, quadruples the area
    perimeter = 2 * (40 + 30)
    lap = R(perimeter, 4)
    laps = R(7 * 60) / lap
    return _case([40, 30, 4, 7],
                 [perimeter == 140, lap == R(35), laps == 12, 2 * (80 + 60) == 2 * perimeter, 80 * 60 == 4 * 40 * 30])


def e10_3_11():  # profit is sales minus expenses, and a higher sale can still mean a lower profit
    data = {'jan': (12000, 9000), 'feb': (15000, 10500), 'mar': (14000, 11200)}
    profit = {m: s - e for m, (s, e) in data.items()}
    return _case(['12,000', '9,000', '15,000', '10,500', '14,000', '11,200'],
                 [profit == {'jan': 3000, 'feb': 4500, 'mar': 2800}, R(profit['feb'], 15000) == R(3, 10),
                  data['mar'][0] > data['jan'][0], profit['mar'] < profit['jan']])


def e10_3_12():  # two linear fares and the break-even kilometre
    a, b = 10 + 4 * x, 5 * x
    km = sp.solve(sp.Eq(a, b), x)[0]
    return _case([10, 4, 5, 14],
                 [km == 10, a.subs(x, km) == 50, b.subs(x, km) == 50, a.subs(x, 14) == 66, b.subs(x, 14) == 70,
                  a.subs(x, 14) < b.subs(x, 14)])


def e10_3_13():  # profit on cost with a discounted batch
    cost = 50 * 80
    discounted = 120 * R(80, 100)
    income = 30 * 120 + 20 * discounted
    profit = income - cost
    return _case([50, 80, 30, 120, 20],
                 [cost == 4000, discounted == 96, income == 5520, profit == 1520, R(profit, cost) == R(38, 100),
                  R(profit, income) != R(profit, cost)])


def e10_3_14():  # weighted mean of two departments, plain mean of the two means is wrong
    weighted = R(4 * 5500 + 2 * 7000, 6)
    sales = [5000, 5000, 5500, 6500]
    median = R(sorted(sales)[1] + sorted(sales)[2], 2)
    return _case(['5,500', '7,000', '5,000', '6,500'],
                 [weighted == 6000, R(5500 + 7000, 2) == 6250, weighted != 6250, sum(sales) == 4 * 5500,
                  median == R(5000 + 5500, 2), max(set(sales), key=sales.count) == 5000])


# ----------------------------------------------------------------------------- 4 units
def e10_4_01():  # distance, midpoint, perpendicular bisector, the point (12, 0) on it
    A, B = sp.Point(1, 2), sp.Point(7, 10)
    dist = A.distance(B)
    mid = A.midpoint(B)
    slope = R(10 - 2, 7 - 1)
    line = -1 / slope * (x - mid.x) + mid.y
    C = sp.Point(12, 0)
    return _case(['A(1, 2)', 'B(7, 10)', 100, 'C(12, 0)'],
                 [dist == 10, dist * 100 == 1000, mid == sp.Point(4, 6), sp.expand(line) == -R(3, 4) * x + 9,
                  line.subs(x, 12) == 0, C.distance(A) == C.distance(B)])


def e10_4_02():  # ball: landing time, maximum, solving h > 15
    h = -5 * t ** 2 + 20 * t
    roots = sp.solve(h, t)
    vertex = sp.solve(sp.diff(h, t), t)[0]
    inequality = sp.solve_univariate_inequality(h > 15, t, relational=False)
    return _case(['-5t² + 20t', 15],
                 [sorted(roots) == [0, 4], vertex == 2, h.subs(t, vertex) == 20, inequality == sp.Interval.open(1, 3),
                  sp.solve_univariate_inequality(t ** 2 - 4 * t + 3 < 0, t, relational=False) == sp.Interval.open(1, 3)])


def e10_4_03():  # roof triangle: similarity ratio, DE, areas
    ratio = R(6, 6 + 3)
    de = ratio * 15
    area = 54 * ratio ** 2
    sin_b = R(2 * 54, 9 * 15)  # the area 54 with AB = 9 and BC = 15 needs sin B = 0.8: a real triangle
    return _case([6, 3, 15, 54],
                 [ratio == R(2, 3), de == 10, area == 24, 54 * ratio != area, 54 * ratio == 36, 0 < sin_b <= 1])


def e10_4_04():  # parabola shifts: vertex, roots of h, h is not even
    h = -(x - 3) ** 2 + 4
    roots = sorted(sp.solve(h, x))
    return _case([3, 4],
                 [roots == [1, 5], sp.diff(h, x).subs(x, 3) == 0, h.subs(x, 3) == 4, h.subs(x, 1) == 0,
                  h.subs(x, -1) == -12, h.subs(x, -1) != h.subs(x, 1)])


def e10_4_05():  # ladder at 60 degrees; a calculator in radian mode gives sin(60) = -0.3048
    height = 5 * sp.sin(sp.pi / 3)
    base = 5 * sp.cos(sp.pi / 3)
    return _case([5, 60],
                 [sp.simplify(height - 5 * sp.sqrt(3) / 2) == 0, base == R(5, 2), sp.simplify(height ** 2 + base ** 2) == 25,
                  round(float(sp.sin(60)), 4) == -0.3048])


def e10_4_06():  # mountain road: extrema, closed interval
    h = x ** 3 - 6 * x ** 2 + 9 * x
    d = sp.diff(h, x)
    zeros = sorted(sp.solve(d, x))
    return _case(['x³ - 6x² + 9x', 0, 4],
                 [zeros == [1, 3], h.subs(x, 1) == 4, h.subs(x, 3) == 0, h.subs(x, 0) == 0, h.subs(x, 4) == 4,
                  d.subs(x, 0) > 0, d.subs(x, 2) < 0, d.subs(x, 3.5) > 0])


def e10_4_07():  # right triangle: median to the hypotenuse, centroid, areas, altitude
    hyp = sp.sqrt(6 ** 2 + 8 ** 2)
    median = hyp / 2
    area = R(6 * 8, 2)
    altitude = 2 * area / hyp
    return _case([6, 8, 10],
                 [hyp == 10, median == 5, R(2, 3) * median == R(10, 3), area == 24, area / 2 == 12,
                  altitude == R(24, 5), altitude != median])


def e10_4_08():  # sqrt function: tangent at x=3 and the extraneous root of sqrt(x+6)=x
    f = sp.sqrt(x + 6)
    slope = sp.diff(f, x).subs(x, 3)
    tangent = f.subs(x, 3) + slope * (x - 3)
    candidates = sorted(sp.solve(sp.Eq(x + 6, x ** 2), x))
    return _case(['√(x + 6)', 3],
                 [f.subs(x, 3) == 3, slope == R(1, 6), sp.expand(tangent) == x / 6 + R(5, 2), candidates == [-2, 3],
                  sp.sqrt(-2 + 6) != -2, sp.sqrt(3 + 6) == 3])


def e10_4_09():  # waiting times: mean, median, mode, range, variance, quartiles
    data = [3, 5, 6, 6, 7, 8, 9, 10, 12, 14]
    n = len(data)
    mean = R(sum(data), n)
    variance = sum((v - mean) ** 2 for v in data) / n
    lower, upper = data[:5], data[5:]
    return _case(['3، 5، 6، 6، 7، 8، 9، 10، 12، 14', 10, 8, 1],
                 [mean == 8, R(data[4] + data[5], 2) == R(15, 2), max(set(data), key=data.count) == 6, max(data) - min(data) == 11,
                  variance == 10, sorted(lower)[2] == 6, sorted(upper)[2] == 10, sp.sqrt(variance) > 1])


def e10_4_10():  # tree of probabilities and Bayes
    p_bad = R(60, 100) * R(5, 100) + R(40, 100) * R(10, 100)
    p_a_given_bad = R(60, 100) * R(5, 100) / p_bad
    return _case(['60%', '40%', '5%', '10%'],
                 [p_bad == R(7, 100), p_a_given_bad == R(3, 7), p_a_given_bad != R(5, 100), R(600 * 5, 100) == 30,
                  R(400 * 10, 100) == 40])


def e10_4_11():  # grouped errors: mean, probability, two students without replacement, median below the mean
    errors = {0: 10, 1: 15, 2: 10, 3: 5}
    n = sum(errors.values())
    mean = R(sum(k * v for k, v in errors.items()), n)
    values = sorted(k for k, v in errors.items() for _ in range(v))
    return _case([40, 10, 15, 5],
                 [n == 40, mean == R(5, 4), R(errors[0] + errors[1] + errors[2], n) == R(7, 8),
                  R(10, 40) * R(9, 39) == R(3, 52), R(values[19] + values[20], 2) == 1, mean > 1])


# ----------------------------------------------------------------------------- 5 units
def e10_5_01():  # circle x^2 + y^2 = 25 and the line y = x + 1
    y = sp.Symbol('y', real=True)
    points = sorted(sp.solve([x ** 2 + y ** 2 - 25, y - x - 1], [x, y]))
    length = sp.sqrt((3 + 4) ** 2 + (4 + 3) ** 2)
    return _case(['x² + y² = 25', 'H1(4, 3)', 'H2(4, 4)', 'y = x + 1', 'x = 6'],
                 [points == [(-4, -3), (3, 4)], 4 ** 2 + 3 ** 2 == 25, 4 ** 2 + 4 ** 2 > 25, length == 7 * sp.sqrt(2),
                  sp.solve(6 ** 2 + y ** 2 - 25, y) == []])


def e10_5_02():  # parabola: intercepts, vertex, the minimum value is -9, not 2
    f = x ** 2 - 4 * x - 5
    roots = sorted(sp.solve(f, x))
    return _case(['x² - 4x - 5'],
                 [roots == [-1, 5], f.subs(x, 0) == -5, sp.solve(sp.diff(f, x), x) == [2], f.subs(x, 2) == -9,
                  sp.solve_univariate_inequality(f > 0, x, relational=False) == sp.Union(sp.Interval.open(-oo, -1), sp.Interval.open(5, oo))])


oo = sp.oo


def e10_5_03():  # centroid 2:1, midline of a trapezoid, converse of Pythagoras
    return _case([15, 8, 14, 9, 12],
                 [R(2, 3) * 15 == 10, R(1, 3) * 15 == 5, R(8 + 14, 2) == 11, 9 ** 2 + 12 ** 2 == 15 ** 2])


def e10_5_04():  # g = 2(x-1)^2 - 8 and h = |g|; sqrt((x-1)^2) = |x-1|
    g = 2 * (x - 1) ** 2 - 8
    roots = sorted(sp.solve(g, x))
    return _case(['2(x - 1)² - 8', 'x = 0'],
                 [roots == [-1, 3], g.subs(x, 1) == -8, abs(g.subs(x, 1)) == 8, g.subs(x, 0) == -6, abs(g.subs(x, 0)) == 6,
                  sp.sqrt((-1 - 1) ** 2) == 2, sp.sqrt((-1 - 1) ** 2) != -1 - 1])


def e10_5_05():  # Thales and the angle bisector theorem
    ec = R(6 * 6, 4)
    de = R(4, 4 + 6) * 20
    bf = R(12, 12 + 18) * 20
    fc = R(18, 12 + 18) * 20
    return _case([4, 6, 20, 12, 18],
                 [ec == 9, de == 8, bf == 8, fc == 12, R(4, 6) == R(6, ec), R(4, 6) != R(ec, 6), 12 + 18 > 20])


def e10_5_06():  # cubic on a closed interval
    f = x ** 3 - 3 * x ** 2 - 9 * x + 5
    d = sp.diff(f, x)
    zeros = sorted(sp.solve(d, x))
    values = {v: f.subs(x, v) for v in (-2, -1, 3, 4)}
    return _case(['x³ - 3x² - 9x + 5', -2, 4],
                 [zeros == [-1, 3], d.subs(x, 0) == -9, f.subs(x, 0) == 5, values[-1] == 10, values[3] == -22,
                  values[-2] == 3, values[4] == -15, max(values.values()) == 10, min(values.values()) == -22,
                  sp.diff(x ** 3, x).subs(x, 0) == 0])


def e10_5_07():  # similar triangles (AA: the right angles, and the angles at A and D); the givens of ABC agree with each other
    ab, bc, ac, de = 6, 8, 10, 9
    perimeter, area = ab + bc + ac, R(ab * bc, 2)  # the right angle is at B, between AB and BC
    k = R(de, ab)  # DE corresponds to AB (D to A, E to B)
    return _case(['AB = 6', 'BC = 8', 'AC = 10', '∠B = 90°', '∠E = 90°', 'DE = 9', '24 × (3/2) = 36'],
                 [ab ** 2 + bc ** 2 == ac ** 2, perimeter == 24, area == 24, k == R(3, 2), perimeter * k == 36, area * k ** 2 == 54,
                  area * k == 36, area * k != area * k ** 2])


def e10_5_08():  # positive does not mean increasing
    f = x ** 3 - 3 * x
    d = sp.diff(f, x)
    return _case(['x³ - 3x'],
                 [sorted(sp.solve(d, x)) == [-1, 1], f.subs(x, R(-1, 2)) > 0, d.subs(x, R(-1, 2)) < 0, d.subs(x, 2) > 0,
                  f.subs(x, -1) == 2, f.subs(x, 1) == -2])


def e10_5_09():  # circle theorems
    cab = 35
    acb = 90
    cba = 180 - acb - cab
    return _case([26, 35],
                 [acb == 90, cba == 55, 2 * cab == 70, 90 - cba == 35, 90 - cba == cab])


def e10_5_10():  # root function: domain, maximum, extraneous solution
    f = sp.sqrt(8 * x - x ** 2)
    zeros = sorted(sp.solve(8 * x - x ** 2, x))
    d = sp.diff(f, x)
    candidates = sorted(sp.solve(sp.Eq(2 * x + 3, x ** 2), x))
    return _case(['√(8x - x²)', '√(2x + 3)'],
                 [zeros == [0, 8], sp.solve(sp.numer(sp.together(d)), x) == [4], f.subs(x, 4) == 4,
                  candidates == [-1, 3], sp.sqrt(2 * 3 + 3) == 3, sp.sqrt(2 * -1 + 3) != -1])


def e10_5_11():  # h(t) = 12 + 10 sin(pi t / 6)
    h = 12 + 10 * sp.sin(sp.pi * t / 6)
    return _case(['12 + 10·sin(πt / 6)', 17, 12],
                 [h.subs(t, 3) == 22, h.subs(t, 9) == 2, sp.simplify(h.subs(t, 0) - h.subs(t, 12)) == 0,
                  sp.simplify(h.subs(t, 1) - 17) == 0, sp.simplify(h.subs(t, 5) - 17) == 0,
                  sp.simplify(h.subs(t, 13) - 17) == 0, sp.simplify(h.subs(t, 17) - 17) == 0])


def e10_5_12():  # cosine rule, area, sine rule with an impossible obtuse angle
    c = sp.sqrt(5 ** 2 + 8 ** 2 - 2 * 5 * 8 * sp.cos(sp.pi / 3))
    area = R(1, 2) * 5 * 8 * sp.sin(sp.pi / 3)
    sin_a = 5 * sp.sin(sp.pi / 3) / 7
    angle_a = sp.deg(sp.asin(sin_a))
    return _case([5, 8, 60],
                 [c == 7, sp.simplify(area - 10 * sp.sqrt(3)) == 0, sp.simplify(sin_a - 5 * sp.sqrt(3) / 14) == 0,
                  round(float(angle_a), 1) == 38.2, 180 - float(angle_a) + 60 > 180])


def e10_5_13():  # a rational function with a removable discontinuity
    g = (2 * x - 6) / (x ** 2 - 9)
    simple = sp.cancel(g)
    return _case(['(2x - 6) / (x² - 9)', 3],
                 [sp.simplify(simple - 2 / (x + 3)) == 0, sp.denom(sp.together(g)).subs(x, 3) == 0, sp.limit(g, x, 3) == R(1, 3),
                  sp.limit(g, x, sp.oo) == 0, sp.limit(g, x, -3, '+') == sp.oo, sp.diff(simple, x) == -2 / (x + 3) ** 2])


SOLUTIONS = {'m' + name[1:].replace('_', '-'): fn for name, fn in globals().items()
             if name.startswith('e10_') and callable(fn)}


# the grade 11 and grade 12 banks are in their own files; one table for the whole example bank
import os as _os
import sys as _sys

_sys.path.insert(0, _os.path.dirname(_os.path.abspath(__file__)))
import example_solutions_11 as _g11  # noqa: E402
import example_solutions_12 as _g12  # noqa: E402

SOLUTIONS.update(_g11.SOLUTIONS)
SOLUTIONS.update(_g12.SOLUTIONS)
