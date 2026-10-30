# Bagrut-style examples, Grade 10, 5 units

Each example here is one question in the **format** of the Bagrut questions: a story (or a function directly, like the differential calculus questions in the Bagrut), parts a b c, and a "justify" part. The stories and the numbers are new, not copied from any exam. The numbers of the examples were checked with sympy (tests/kit/example_solutions.py).

## m10-5-01 Introduction to analytic geometry (מבוא לגאומטריה אנליטית)

**The story:** a transmission tower at the origin O(0, 0), and its coverage area is the circle x² + y² = 25 (the unit is a kilometer).

**Part a (5 marks):** decide for each house whether it is inside the coverage area, on its border, or outside it: H1(4, 3) and H2(4, 4).

**Part b (6 marks):** a road whose equation is y = x + 1. Find its two intersection points with the border of the coverage area.

**Part c (5 marks):** find the length of the part of the road that is inside the coverage area (in exact form).

**Part d (4 marks) - justify:** another road whose equation is x = 6. Does it cross the border of the coverage? Justify, and is this equation a function?

## m10-5-02 Introduction to function analysis (קדם אנליזה)

**The story:** the function f(x) = x² - 4x - 5 describes the profit of a store in thousands of shekels (and negative is a loss), as a function of the time x in years from the beginning of the year 2020 (x = -1 means the year 2019).

**Part a (5 marks):** find the intersection points of f with the two axes.

**Part b (5 marks):** find the vertex of the curve, and the intervals where it is increasing and decreasing.

**Part c (4 marks):** find the range of values where f(x) is positive.

**Part d (4 marks) - justify:** a student said: "The smallest value of the function is 2". What is he mixing up? And what is correct?

## m10-5-03 Geometry: review and completions (גאומטריה: חזרה והשלמות)

**The story:** a garden in the shape of a triangle ABC, and its median AD is 15 m long. The point M is the meeting point of the three medians.

**Part a (5 marks):** find AM and MD.

**Part b (4 marks):** next to the garden there is a path in the shape of a trapezoid whose bases are 8 m and 14 m. Find the length of the segment connecting the midpoints of its legs.

**Part c (5 marks) - justify:** a triangle whose sides are 9 m and 12 m and 15 m. Is it a right triangle? Justify with a suitable theorem.

## m10-5-04 Power functions and transformations (פונקציות חזקה)

**The story:** an animation designer draws on the screen (the origin is in its middle, so the coordinates can be negative). He uses f(x) = x² as the base of a path, and makes from it g(x) = 2(x - 1)² - 8.

**Part a (5 marks):** find the vertex of g, the direction in which it opens, and its intercepts with the x axis.

**Part b (5 marks):** h(x) = |g(x)|. Find h at the vertex and at x = 0, and say where h is different from g.

**Part c (5 marks) - justify:** a student wrote √((x - 1)²) = x - 1 for every x. Give an example that shows the mistake, and what is correct?

## m10-5-05 Proportion and Thales' theorem (פרופורציה, משפט תאלס)

**The story:** the roof of a house in the shape of a triangle ABC. The point D is on AB, and the point E is on AC, and DE is parallel to BC. AD = 4 m, DB = 6 m, AE = 6 m, BC = 20 m.

**Part a (4 marks):** find EC.

**Part b (4 marks):** find DE.

**Part c (6 marks):** in another triangle AB = 12 m and AC = 18 m and BC = 20 m, the bisector of the angle A cuts BC at the point F. Find BF and FC.

**Part d (4 marks) - justify:** a student wrote AD / DB = EC / AE. Where is the mistake?

## m10-5-06 Differentiation: the derivative (חשבון דיפרנציאלי)

**The story:** the temperature in degrees Celsius in a test room as a function of the time x in hours from the moment the cooling device is switched on (x = 0) is f(x) = x³ - 3x² - 9x + 5. The measurement started two hours before the switch-on and continues until the fourth hour: -2 ≤ x ≤ 4.

**Part a (5 marks):** find f'(x), and find the equation of the tangent to the curve f at x = 0.

**Part b (5 marks):** find the local extremum points and their type.

**Part c (5 marks):** find the greatest and the smallest value of f on the closed interval [-2, 4].

**Part d (4 marks) - justify:** is every point that satisfies f'(x) = 0 an extremum? Give an example with another function.

## m10-5-07 Similarity of triangles (דמיון משולשים)

**The story:** in a triangle ABC, AB = 6 cm, BC = 8 cm, AC = 10 cm and ∠B = 90°. In a triangle DEF, ∠E = 90°, ∠D = ∠A and DE = 9 cm. The perimeter of ABC = 24 cm and its area is 24 square cm.

**Part a (5 marks):** prove that ABC ~ DEF, and find the similarity ratio.

**Part b (4 marks):** find the perimeter of DEF.

**Part c (5 marks):** find the area of DEF.

**Part d (4 marks) - justify:** a student said that the area of DEF = 24 × (3/2) = 36. Where is the mistake?

## m10-5-08 Graph and derivative (גרף ונגזרת)

**The story:** the function f(x) = x³ - 3x describes the height of a path in a game relative to the middle of the screen (negative values are below the middle of the screen). The graph of f' (the derivative) is drawn below the graph of f, on other axes.

**Part a (4 marks):** find f'(x) and its zeros.

**Part b (5 marks):** from the sign of f', find the intervals where it is increasing and decreasing and the extremum points.

**Part c (5 marks) - justify:** your friend said: "f is positive on the interval (-1, 0), so it is increasing there". Is he right? Justify with a calculation.

## m10-5-09 The circle (המעגל)

**The story:** a Ferris wheel whose center is O. The segment AB is a diameter of it (its length is 26 m), and the point C is a cabin on the rim of the wheel, and ∠CAB = 35°.

**Part a (4 marks):** find ∠ACB, and justify.

**Part b (4 marks):** find ∠CBA.

**Part c (4 marks):** find the central angle ∠COB, and justify.

**Part d (5 marks) - justify:** the tangent to the circle at B makes an acute angle with the chord BC. Find its size, and justify with the theorem of the angle between a tangent and a chord.

## m10-5-10 The root function (פונקציית שורש)

**The story:** an arch at the entrance of a building, and its height in meters is f(x) = √(8x - x²) at a distance of x meters from the start of the arch.

**Part a (4 marks):** find the domain of f.

**Part b (6 marks):** find f'(x), the extremum point, and the highest height of the arch.

**Part c (5 marks):** solve the equation √(2x + 3) = x.

**Part d (4 marks) - justify:** why must we substitute the solutions into the original equation after squaring?

## m10-5-11 The trigonometric functions (הפונקציות הטריגונומטריות)

**The story:** the height of a cabin of a Ferris wheel in meters above the ground after t minutes is h(t) = 12 + 10·sin(πt / 6).

**Part a (4 marks):** find the highest and the lowest height of the cabin.

**Part b (4 marks):** find the period (how many minutes for a full turn?).

**Part c (6 marks):** when is the height 17 meters during the first cycle 0 ≤ t ≤ 12?

**Part d (4 marks) - justify:** a student found only t = 1. Why is he missing a solution, and what is the general solution?

## m10-5-12 Trigonometry in the plane (טריגונומטריה במישור)

**The story:** a triangular plot ABC in which BC = 5 m and CA = 8 m, and the angle between them is C = 60°.

**Part a (5 marks):** find the length of AB.

**Part b (4 marks):** find the area of the plot (in exact form).

**Part c (5 marks):** use the law of sines to find sin A, and then the angle A to the nearest tenth of a degree.

**Part d (4 marks) - justify:** why is it rejected that A is obtuse (a second value that satisfies the same sin)?

## m10-5-13 The rational function (פונקציה רציונלית)

**The story:** a question without a story, like the differential calculus chapter in the exam: the function g(x) = (2x - 6) / (x² - 9).

**Part a (3 marks):** find the domain of g.

**Part b (6 marks):** find the vertical and horizontal asymptotes, and the point of discontinuity if there is one.

**Part c (5 marks):** find g'(x), and decide whether g is increasing or decreasing.

**Part d (4 marks) - justify:** why is x = 3 not a vertical asymptote even though it makes the denominator zero?
