# Exam-style examples, Grade 11, 5 units

Each example here is one question in the **format** of the exam questions: a story (or a function directly, like the differential calculus questions in the exam), parts a b c, and a "justify" part. The stories and the numbers are new, not copied from any exam. The numbers of the examples were checked with sympy (tests/kit/example_solutions_11.py).

## m11-5-01 Trigonometric functions (פונקציות טריגונומטריות)

**The story:** the height of the tide water in meters above the bottom of the harbor after t hours from midnight is h(t) = 2 + 2·sin(πt / 6), for 0 ≤ t ≤ 12.

**Part a (4 marks):** find the highest and the lowest height of the water.

**Part b (5 marks):** when is the height 1 meter?

**Part c (6 marks) - justify:** solve the equation h(t)² = 2·h(t). A student divided both sides by h(t) and got only t = 0 and t = 6 and t = 12. Which solution was lost, and why?

## m11-5-02 Differential calculus (חשבון דיפרנציאלי)

**The story:** the amount of water in a reservoir in cubic meters after t hours is V(t) = t³ - 6t² + 9t + 1, for 0 ≤ t ≤ 4.

**Part a (5 marks):** find V'(t) and V''(t).

**Part b (5 marks):** find the inflection point, and state the interval where it is concave down and the interval where it is concave up.

**Part c (5 marks) - justify:** is every point that satisfies f''(x) = 0 an inflection point? Give an example with another function.

## m11-5-03 Sequences (סדרות)

**The story:** a ball falls from a height of 48 cm, and after each bounce it reaches half of the previous height. The heights of the bounces (48, 24, 12, ...) are a geometric sequence.

**Part a (4 marks):** find the height at the fourth bounce.

**Part b (5 marks):** find the sum of the first 4 heights.

**Part c (6 marks) - justify:** find the sum of all the heights if the ball kept bouncing forever. Why can we not use the same formula for the sequence 2, 4, 8, ...?

## m11-5-04 Extreme value problems (בעיות קיצון)

**The story:** a farmer has 40 m of fence, and wants to fence 3 sides of a rectangular plot, and the fourth side is a wall. The width of the plot is x m (the two lateral sides).

**Part a (5 marks):** write the area of the plot A(x) in terms of x.

**Part b (4 marks):** find the domain of x that fits the problem.

**Part c (6 marks) - justify:** find the largest area, and justify that it is a maximum value, and that it is inside the domain.

## m11-5-05 Mathematical induction (אינדוקציה מתמטית)

**The story:** a question without a story: prove by induction that 1 + 3 + 5 + ... + (2n - 1) = n² for every natural n.

**Part a (4 marks):** check that the claim is true for n = 1.

**Part b (6 marks):** assume it is true for n = k, and prove that it is true for n = k + 1.

**Part c (5 marks) - justify:** the claim "n² + n + 41 is a prime number for every n" is true for n = 1 up to 39. Why is this not a proof, and which n breaks it?

## m11-5-06 Differentiating trigonometric functions (גזירת פונקציות טריגונומטריות)

**The story:** the height of a wave in meters above sea level is h(t) = 10 + sin t + cos t, for 0 ≤ t ≤ π (t in radians).

**Part a (4 marks):** find h'(t).

**Part b (6 marks):** find the highest height in the interval, and when it happens.

**Part c (5 marks) - justify:** a student wrote that the derivative of sin(3t) is cos(3t). Where is the mistake, and what is correct?

## m11-5-07 Probability (הסתברות)

**The story:** a test of 5 true/false questions, and a student guesses all the answers (the probability of correct for each question is 1/2, and the questions are independent).

**Part a (5 marks):** find the probability that he answers exactly 3 questions correctly.

**Part b (5 marks):** find the probability that he answers 4 questions correctly or more, and then the probability that he answers all 5 correctly given that he answered 4 or more.

**Part c (5 marks) - justify:** why do we multiply by the binomial coefficient in the Bernoulli formula?

## m11-5-08 Integral calculus (חשבון אינטגרלי)

**The story:** the speed of an object in meters per second is v(t) = 3t² + 2, and its position s(t) satisfies s(1) = 5.

**Part a (5 marks):** find the position function s(t), and the position of the object at t = 0.

**Part b (5 marks):** find the definite integral from 0 to π/2 of the function cos x.

**Part c (5 marks) - justify:** find the area enclosed between y = 4 - x² and the x axis. Why are the limits -2 and 2?

## m11-5-09 Review (חזרות)

**The story:** a student saves 5 ₪ in the first week, and adds 3 ₪ every week compared to the one before (an arithmetic sequence).

**Part a (4 marks):** how much does she save in the tenth week?

**Part b (5 marks):** what is the total of what she saved after 10 weeks?

**Part c (6 marks) - justify:** after how many weeks will the total be at least 500 ₪? Why is 17 weeks not enough?
