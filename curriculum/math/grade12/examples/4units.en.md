# Exam-style examples, Grade 12, 4 units

Each example here is one question in the **format** of the exam questions: a story (or a function directly, like the differential calculus questions in the exam), parts a b c, and a "justify" part. The stories and the numbers are new, not copied from any exam. The numbers of the examples were checked with sympy (tests/kit/example_solutions_12.py).

## m12-4-01 Geometry in space (גאומטריה במרחב)

**The story:** a room in the shape of a cube ABCDEFGH, whose side is 4 m long. A is a corner on the floor, and G is the corner opposite it on the ceiling.

**Part a (4 marks):** express the vector AG as a linear combination of the vectors AB and AD and AE.

**Part b (5 marks):** find the length of the diagonal AG in exact form.

**Part c (5 marks) - justify:** find the length of AC (the diagonal of the floor). Why is AC shorter than AG?

## m12-4-02 The exponential function (פונקציה מעריכית)

**The story:** a bacteria farm whose number after t hours is N(t) = 100 · 2^t, where t ≥ 0.

**Part a (4 marks):** how many bacteria will there be after 3 hours?

**Part b (5 marks):** after how many hours will the number be 6,400?

**Part c (5 marks) - justify:** solve the equation 2^(x+1) + 2^x = 24. Why is 2^x never equal to zero or negative?

## m12-4-03 The dot product, geometric method (מכפלה סקלרית)

**The story:** a force of 3 newtons pulls an object, and the object moves 4 m, and the angle between the direction of the force and the direction of the motion is 60°. The work = the dot product of the force and the displacement.

**Part a (4 marks):** find the work in joules.

**Part b (5 marks):** if a and b are vectors with these same two magnitudes and the same angle, find |a + b|.

**Part c (5 marks) - justify:** when is the dot product of two non-zero vectors equal to zero? What does it mean geometrically?

## m12-4-04 The logarithmic function (פונקציה לוגריתמית)

**The story:** a question without a story: the equation log₂(x) + log₂(x - 2) = 3.

**Part a (5 marks):** solve the equation.

**Part b (4 marks) - justify:** why is one of the two solutions that come out when squaring rejected?

**Part c (5 marks) - justify:** a student wrote log₂(x + y) = log₂ x + log₂ y. Give a numerical example that shows it is wrong.

## m12-4-05 A line or a vector perpendicular to a plane (ישר מאונך למישור)

**The story:** a glass right pyramid whose base is a square with a side of 6 m, and whose height (the perpendicular from the apex to the center of the base) is 4 m.

**Part a (4 marks):** find the volume of the pyramid.

**Part b (5 marks):** find the height of the lateral face (from the apex to the midpoint of a side of the base).

**Part c (5 marks) - justify:** find the lateral area. Why do we use half of the side (3 m) in Pythagoras and not the whole side?

## m12-4-06 Coordinate system in space and algebraic representation of vectors (מערכת צירים במרחב וייצוג אלגברי של וקטורים)

**The story:** on a three-dimensional model of a building, the points A(1, 2, 3) and B(4, 6, 3) and C(1, 2, 7).

**Part a (4 marks):** find the vector AB and its length.

**Part b (4 marks):** find the coordinates of the midpoint of AB.

**Part c (5 marks) - justify:** is AB perpendicular to AC? Justify with the dot product.

## m12-4-07 Operations on vectors and the dot product, algebraic method (פעולות על וקטורים ומכפלה סקלרית בדרך אלגברית)

**The story:** a question without a story: the vectors a = (2, 1, -2) and b = (1, 2, 2) and c = (1, 0, 0).

**Part a (4 marks):** find a · b, and say what it means.

**Part b (4 marks):** find |a| and |b|.

**Part c (5 marks) - justify:** find the cosine of the angle between a and c. Why do we not need to know the angle itself to say that it is acute?

## m12-4-08 Mixed problems with vectors, both methods (שאלות משולבות בוקטורים בשתי הדרכים)

**The story:** a cube whose side is 2 m long, with vertices A(0, 0, 0) and C(2, 2, 0) and G(2, 2, 2).

**Part a (4 marks):** find AG · AC with the algebraic method.

**Part b (5 marks):** find the cosine of the angle CAG, and the angle to the nearest tenth of a degree.

**Part c (5 marks) - justify:** find the same angle with the geometric method (the triangle CAG has a right angle at C). Why does the same answer come out?

## m12-4-09 Growth and decay problems (בעיות גדילה ודעיכה)

**The story:** a radioactive material whose mass is 80 grams, and its half-life is 5 years. The mass after t years is M(t) = 80 · (1/2)^(t/5).

**Part a (4 marks):** find the mass after 10 years.

**Part b (5 marks):** after how many years will the mass be 5 grams?

**Part c (5 marks) - justify:** why does the mass get smaller every time but never reach zero?

## m12-4-10 Sequences (סדרות)

**The story:** a boy saves 3 ₪ in the first week, and then adds 4 ₪ every week (an arithmetic sequence). And another sequence is geometric, with a first term of 2 and a ratio of 3.

**Part a (4 marks):** find the amount in the tenth week.

**Part b (5 marks):** find the total of what he saved after 10 weeks.

**Part c (5 marks) - justify:** find the fifth term and the sum of the first 5 terms of the geometric sequence. Why does its infinite sum not exist?

## m12-4-11 Differentiating the exponential function with base e (גזירת הפונקציה המעריכית בבסיס e)

**The story:** a question without a story: the function f(x) = x · e^x.

**Part a (5 marks):** find f'(x).

**Part b (5 marks):** find the smallest value of f, and when it happens.

**Part c (5 marks) - justify:** find the equation of the tangent at x = 0. Why is the sign of f' the same as the sign of (x + 1)?

## m12-4-12 Differentiating the logarithmic function with base e (גזירת הפונקציה הלוגריתמית בבסיס e)

**The story:** a question without a story: the function f(x) = x - ln x.

**Part a (4 marks):** find the domain.

**Part b (5 marks):** find f'(x) and the local extremum point and its type.

**Part c (5 marks) - justify:** find the equation of the tangent at x = e. Why must we check the domain before we investigate the function?

## m12-4-13 Integral calculus (חשבון אינטגרלי)

**The story:** the growth rate of a bacteria farm in thousands of bacteria per hour is r(t) = e^t, where t ≥ 0.

**Part a (5 marks):** find the increase in the number (in thousands) during the period from t = 0 to t = ln 3.

**Part b (5 marks):** find the definite integral from 1 to e of the function 1/x.

**Part c (5 marks) - justify:** if the number at t = 0 was 3 thousand, find the function of the number N(t). What does the constant C mean here?

## m12-4-14 Review (חזרות)

**The story:** a question without a story: the function f(x) = e^(2x) - 3e^x + 2.

**Part a (5 marks):** solve the equation f(x) = 0.

**Part b (5 marks):** find the smallest value of f.

**Part c (4 marks) - justify:** why does the equation e^x = -1 have no solution?
