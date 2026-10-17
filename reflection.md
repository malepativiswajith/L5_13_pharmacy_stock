# Reflection — Lab 5: Static Code Analysis

**Note:** The supplied handout explains the lab objectives and deliverables but does not list the four reflection questions verbatim. The answers below address four reflection topics aligned with the handout; replace the headings if your instructor has provided a separate question sheet.

## 1. What is static code analysis, and why is it useful?

Static code analysis checks source code without needing to run the program. Pylint focuses on code quality and common programming mistakes, Flake8 checks style and formatting, and Bandit looks for common security risks. These tools help detect problems early, make code easier to maintain, and provide repeatable checks after changes.

## 2. What important issues did you find?

The most serious issue was SQL injection in the patient lookup because user input was inserted directly into an SQL statement. The dispensing logic also did not verify stock quantity before subtracting units, which could create negative stock. The code used a mutable default list and broad exception handlers, and it could report already-expired medicine as expiring soon. Some of these are logic problems that require reading and testing the program; a linter will not necessarily identify every one.

## 3. How did you fix the issues?

I changed the patient query to use SQL parameters, removed broad exception handling, and added checks for patient existence, medicine existence, positive quantities, sufficient stock, and expiry dates before dispensing. I replaced the mutable default argument with `None`, used `with` statements for file handling, handled expected file and JSON errors, normalized allergy comparisons, and corrected the expiry-date filter. I also renamed `printStock` to `print_stock` and corrected the demo's negative stock addition.

## 4. What did you learn, and what are the limitations of static analysis?

I learned that Pylint, Flake8, and Bandit serve different purposes, so using all three gives broader coverage than relying on one tool. Static analysis can find many suspicious patterns, but it cannot prove that a program behaves correctly for every input. Logical and domain-specific errors still require tests and careful review. After making changes, I should rerun all tools, compare the reports, test the program with valid and invalid inputs, and record the actual results rather than assuming that a fix worked.
