"""Independent sympy solutions for the hard eval cases (tests/evals/tutor_cases.json, tier "hard").

Each function recomputes the case from its problem statement. `answers` must equal the
case's `math.expected`; `facts` must all be True (the student's wrong step really is wrong,
the trap really exists, the "why" example really works). tests/offline/test_run_evals.py
checks both, so a wrong reference answer cannot reach a paid run.
"""
import sympy as sp

x, t = sp.symbols('x t', real=True)
R = sp.Rational
S = sp.S


def _case(answers=(), facts=()):
    return {'answers': list(answers), 'facts': list(facts)}


# ----------------------------------------------------------------- grade 10
def h10u3_1():  # m10-3-13: profit percent is measured on the cost, not on the selling price
    cost = 40 * 50
    revenue = 30 * 90 + 10 * 60
    profit = revenue - cost
    percent = R(profit, cost) * 100
    wrong = R(profit, revenue) * 100
    return _case([percent, percent / 100], [revenue == 3300, profit == 1300, percent == 65, wrong != percent,
                             round(float(wrong), 1) == 39.4])


def h10u3_2():  # m10-3-03: weighted mean differs from the plain mean of two group means
    weighted = R(20 * 80 + 30 * 60, 50)
    plain = R(80 + 60, 2)
    return _case([], [weighted == 68, plain == 70, weighted != plain])


def h10u3_3():  # m10-3-07: average speed = total distance / total time, with minutes converted
    d1 = 60 * R(30, 60)
    d2 = 80 * R(5, 4)
    speed = (d1 + d2) / (R(30, 60) + R(5, 4))
    return _case([speed], [d1 == 30, d2 == 100, speed == R(520, 7), speed != R(60 + 80, 2)])


def h10u4_1():  # m10-4-06: tangent to a cubic, then its x-intercept
    f = x**3 - 3 * x**2 + 5 * x
    slope = sp.diff(f, x).subs(x, 2)
    tangent = slope * (x - 2) + f.subs(x, 2)
    root = sp.solve(tangent, x)[0]
    wrong_slope = (3 * x**2 - 6 * x + 5 * x).subs(x, 2)  # derivative of 5x written as 5x
    wrong_root = sp.solve(wrong_slope * (x - 2) + f.subs(x, 2), x)[0]
    return _case([root], [f.subs(x, 2) == 6, slope == 5, sp.expand(tangent) == 5 * x - 4,
                          wrong_slope == 10, wrong_root == R(7, 5), root == R(4, 5)])


def h10u4_2():  # m10-4-03: areas of similar triangles scale with the square of the ratio
    base, height, k = 4, 5, 3
    area = R(base * height, 2)
    scaled = R(base * k * height * k, 2)
    return _case([], [area == 10, scaled == 90, scaled == k**2 * area, scaled != k * area])


def h10u4_3():  # m10-4-08: squaring both sides, then rejecting the extraneous root
    equation = sp.sqrt(x + 2) - (x - 4)
    squared = sp.expand((x + 2) - (x - 4)**2)
    candidates = sp.solve(squared, x)
    valid = [c for c in candidates if sp.simplify(equation.subs(x, c)) == 0]
    wrong = sp.solve(x + 2 - (x**2 - 16), x)  # (x - 4)^2 written as x^2 - 16
    return _case(valid, [sorted(candidates) == [2, 7], valid == [7], sp.sqrt(4) + 4 != 2,
                         set(wrong) == {(1 + sp.sqrt(73)) / 2, (1 - sp.sqrt(73)) / 2}])


def h10u5_1():  # m10-5-12: law of cosines, then the area with the sine formula
    a, b, angle = 7, 8, sp.pi / 3
    c = sp.sqrt(a**2 + b**2 - 2 * a * b * sp.cos(angle))
    area = R(1, 2) * a * b * sp.sin(angle)
    wrong_c2 = a**2 + b**2 - 2 * a * b  # cos 60 forgotten
    return _case([c, area], [sp.simplify(c**2 - 57) == 0, sp.simplify(area - 14 * sp.sqrt(3)) == 0,
                             wrong_c2 == 1, a + sp.sqrt(wrong_c2) <= b])


def h10u5_2():  # m10-5-11: sin x = 1/2 has two solutions on one turn (unit circle, same y)
    found = sp.solveset(sp.sin(x) - R(1, 2), x, sp.Interval.Ropen(0, 2 * sp.pi))
    return _case([], [found == {sp.pi / 6, 5 * sp.pi / 6}, sp.sin(sp.pi - sp.pi / 6) == sp.sin(sp.pi / 6)])


def h10u5_3():  # m10-5-13: a cancelled factor gives a hole, not a vertical asymptote
    f = (x**2 - 4) / (x**2 - x - 2)
    simplified = sp.cancel(f)
    hole = (2, sp.limit(f, x, 2))
    left, right = sp.limit(f, x, -1, '-'), sp.limit(f, x, -1, '+')
    return _case([hole[1]], [sp.simplify(simplified - (x + 2) / (x + 1)) == 0, hole[1] == R(4, 3),
                             left == -S.Infinity, right == S.Infinity, sp.limit(f, x, 2, '+') == sp.limit(f, x, 2, '-')])


# ----------------------------------------------------------------- grade 11
def h11u3_1():  # m11-3-01: repeated percentage decay is a power, not a sum of percentages
    value = 50000 * R(8, 10)**3
    wrong = 50000 * (1 - R(20, 100) * 3)
    return _case([value, 50000 - value], [value == 25600, 50000 - value == 24400, wrong == 20000, wrong != value])


def h11u3_2():  # m11-3-02: signed deviations cancel; squares do not
    data = [2, 4, 6, 8, 10]
    mean = R(sum(data), len(data))
    deviations = [d - mean for d in data]
    variance = R(sum(d**2 for d in deviations), len(data))
    return _case([], [mean == 6, sum(deviations) == 0, sum(d**2 for d in deviations) == 40,
                      variance == 8, sp.sqrt(variance) == 2 * sp.sqrt(2)])


def h11u3_3():  # m11-3-03: drawing without replacement is not independent
    same = R(5, 8) * R(4, 7) + R(3, 8) * R(2, 7)
    wrong = R(5, 8)**2 + R(3, 8)**2
    return _case([same], [same == R(13, 28), wrong == R(17, 32), wrong != same])


def h11u4_1():  # m11-4-12: area between the curve and the axis needs |.| where the curve is below it
    f = x**2 - 4 * x + 3
    signed = sp.integrate(f, (x, 0, 3))
    area = sp.integrate(f, (x, 0, 1)) + sp.integrate(-f, (x, 1, 3))
    return _case([area], [signed == 0, area == R(8, 3), sp.solve(f, x) == [1, 3]])


def h11u4_2():  # m11-4-04: z-scores put different exams on one scale
    z_a = R(85 - 70, 10)
    z_b = R(58 - 50, 5)
    return _case([], [z_a == R(3, 2), z_b == R(8, 5), z_b > z_a, 85 > 58])


def h11u4_3():  # m11-4-11: ambiguous case of the law of sines (two triangles)
    a, b, A = 6, 6 * sp.sqrt(2), sp.pi / 6
    sin_b = sp.simplify(b * sp.sin(A) / a)
    angles_b = [sp.pi / 4, 3 * sp.pi / 4]
    sides = []
    for B in angles_b:
        C = sp.pi - A - B
        sides.append(sp.simplify(sp.expand_trig(a * sp.sin(C) / sp.sin(A))))
    first = 3 * (sp.sqrt(6) + sp.sqrt(2))
    second = 3 * (sp.sqrt(6) - sp.sqrt(2))
    return _case([second], [sp.simplify(sin_b - sp.sqrt(2) / 2) == 0,
                            sp.simplify(sides[0] - first) == 0, sp.simplify(sides[1] - second) == 0,
                            all(sp.N(B) + sp.N(A) < sp.N(sp.pi) for B in angles_b)])


def h11u5_1():  # m11-5-04: open-box volume, maximum at the root inside the domain
    v = x * (12 - 2 * x)**2
    roots = sp.solve(sp.diff(v, x), x)
    inside = [r for r in roots if 0 < r < 6]
    best = v.subs(x, inside[0])
    wrong = sp.Poly(144 - 48 * x + 12 * x**2, x).discriminant()
    return _case([best], [sp.expand(v) == 4 * x**3 - 48 * x**2 + 144 * x, sorted(roots) == [2, 6],
                          inside == [2], best == 128, sp.diff(v, x, 2).subs(x, 2) < 0, wrong < 0])


def h11u5_2():  # m11-5-02: f'' = 0 without a sign change is not an inflection point
    f4, f3 = x**4, x**3
    second4, second3 = sp.diff(f4, x, 2), sp.diff(f3, x, 2)
    return _case([], [second4.subs(x, 0) == 0, second4.subs(x, R(-1, 2)) > 0, second4.subs(x, R(1, 2)) > 0,
                      second3.subs(x, 0) == 0, second3.subs(x, R(-1, 2)) < 0, second3.subs(x, R(1, 2)) > 0])


def h11u5_3():  # m11-5-03: the ratio of 12, -6, 3, ... is negative
    a1, q = 12, R(-6, 12)
    total = R(a1) / (1 - q)
    wrong = R(a1) / (1 - R(1, 2))
    return _case([total], [q == R(-1, 2), abs(q) < 1, total == 8, wrong == 24, wrong != total])


# ----------------------------------------------------------------- grade 12
def h12u3_1():  # m12-3-03: linear programming optimum is at a feasible vertex
    p = lambda a, b: 30 * a + 20 * b
    corner = sp.solve([x + t - 10, 2 * x + t - 16], [x, t])
    vertices = [(0, 0), (8, 0), (corner[x], corner[t]), (0, 10)]
    best = max(p(a, b) for a, b in vertices)
    return _case([best], [corner == {x: 6, t: 4}, best == 260, p(6, 10) == 380, 6 + 10 > 10])


def h12u3_2():  # m12-3-01: the normal density integrates to 1
    density = sp.exp(-x**2 / 2) / sp.sqrt(2 * sp.pi)
    total = sp.integrate(density, (x, -sp.oo, sp.oo))
    one_sigma = sp.integrate(density, (x, -1, 1))
    return _case([], [sp.simplify(total) == 1, 0.68 < float(one_sigma) < 0.69])


def h12u3_3():  # m12-3-02: vertex gives time and height; the ground time is the positive root
    h = -5 * t**2 + 30 * t + 80
    peak_time = sp.solve(sp.diff(h, t), t)[0]
    peak = h.subs(t, peak_time)
    ground = [r for r in sp.solve(h, t) if r > 0]
    return _case([peak, ground[0]], [peak_time == 3, peak == 125, sorted(sp.solve(h, t)) == [-2, 8], ground == [8]])


def h12u4_1():  # m12-4-04: log a + log b = log(ab); the domain removes x = -2
    equation = sp.log(x, 2) + sp.log(x - 2, 2) - 3
    candidates = sp.solve(x * (x - 2) - 8, x)
    valid = [c for c in candidates if c > 2]
    wrong = sp.solve(2 * x - 2 - 8, x)[0]
    return _case(valid, [sorted(candidates) == [-2, 4], valid == [4], wrong == 5,
                         sp.simplify(equation.subs(x, 4)) == 0, sp.N(equation.subs(x, 5)) != 0])


def h12u4_2():  # m12-4-02: d/dx a^x = a^x ln a, equal to a^x only when ln a = 1
    a = sp.Symbol('a', positive=True)
    derivative = sp.diff(a**x, x)
    return _case([], [sp.simplify(derivative - a**x * sp.log(a)) == 0, sp.solve(sp.log(a) - 1, a) == [sp.E],
                      sp.diff(sp.exp(x), x) == sp.exp(x), 0 < sp.N(sp.log(2)) < 1])


def h12u4_3():  # m12-4-12: the critical point x = 2 is outside the domain of ln(x^2 - 4x + 3)
    inner = x**2 - 4 * x + 3
    critical = sp.solve(sp.diff(sp.log(inner), x), x)
    domain = sp.solveset(inner > 0, x, sp.S.Reals)
    return _case([], [critical == [2], inner.subs(x, 2) == -1, 2 not in domain,
                      domain == sp.Union(sp.Interval.open(-sp.oo, 1), sp.Interval.open(3, sp.oo)),
                      sp.limit(sp.log(inner), x, 1, '-') == -sp.oo])


def h12u5_1():  # m12-5-08: de Moivre raises the modulus as well as multiplying the angle
    z = 1 + sp.I * sp.sqrt(3)
    numerator = sp.simplify(sp.expand(z**6))
    denominator = sp.simplify(sp.expand((1 - sp.I)**4))
    value = sp.simplify(numerator / denominator)
    return _case([value, numerator], [sp.simplify(sp.Abs(z) - 2) == 0, sp.simplify(sp.arg(z) - sp.pi / 3) == 0,
                                      numerator == 64, denominator == -4, value == -16,
                                      R(2) / denominator == R(-1, 2)])


def h12u5_2():  # m12-5-06: a.b = |a||b|cos(theta), so a.b = 0 exactly when the angle is 90 degrees
    a = sp.Matrix([2, 3, 1])
    b = sp.Matrix([1, -1, 1])
    u, v = sp.Matrix(sp.symbols('u1 u2 u3')), sp.Matrix(sp.symbols('v1 v2 v3'))
    law = sp.expand((u - v).dot(u - v) - (u.dot(u) + v.dot(v) - 2 * u.dot(v)))
    return _case([], [a.dot(b) == 0, sp.acos(a.dot(b) / (a.norm() * b.norm())) == sp.pi / 2, law == 0])


def h12u5_3():  # m12-5-05: y = x + sqrt(13) is tangent to x^2/9 + y^2/4 = 1
    k = sp.sqrt(13)
    quadratic = sp.expand(36 * (x**2 / 9 + (x + k)**2 / 4 - 1))
    poly = sp.Poly(quadratic, x)
    point_x = sp.solve(quadratic, x)
    px = sp.simplify(point_x[0])
    py = sp.simplify(px + k)
    wrong = sp.expand(4 * x**2 + 9 * (x**2 + 13) - 36)
    return _case([px, py], [sp.simplify(poly.discriminant()) == 0, len(point_x) == 1,
                            sp.simplify(px - (-9 * k / 13)) == 0, sp.simplify(py - 4 * k / 13) == 0,
                            sp.simplify(px**2 / 9 + py**2 / 4 - 1) == 0, wrong == 13 * x**2 + 81,
                            sp.solve(wrong, x, dict=False) != point_x])


# Case ids use dashes (h10u3-1); function names use underscores.
SOLUTIONS = {name.replace('_', '-'): fn for name, fn in globals().items() if name.startswith('h1') and callable(fn)}
