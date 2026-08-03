---
layout: default
title: C++ Refactoring & TDD
permalink: /code-reviewer-agent/cpp-refactoring-tdd/
---
# C++ Refactoring & TDD

Notes on applying refactoring and TDD to the [interpreter kata](/code-reviewer-agent/interpreter/), tying together the Clean Code / Refactoring course material with actual practice.

## Red-Green-Refactor, Applied to C++

- **Red** — write a failing test for one grammar rule or one evaluation case at a time (e.g. `2 + 3 * 4` respects precedence) before writing the code for it.
- **Green** — write the minimum interpreter code to pass, even if it's ugly (a growing `if`/`else` chain in the evaluator is fine at this stage).
- **Refactor** — only once green, clean up: extract the token type into an enum, replace an `if`/`else` chain with a `switch` or visitor, pull duplicated parsing logic into a helper.

## C++-Specific Refactoring Moves Used Here

- **RAII over manual cleanup** — token/AST-node ownership via `std::unique_ptr` instead of raw `new`/`delete`, so failing tests don't also leak memory.
- **Replace conditional with polymorphism** — once the evaluator's `switch` on node type grows past a handful of cases, move to a small visitor or virtual `evaluate()` per node type.
- **Extract function** — pull the "current token lookahead" logic in the parser into its own method once it starts getting duplicated across grammar rules.
- **Introduce parameter object** — bundle parser state (tokens, position, error list) instead of passing them around individually as the parser grows.

## Test Setup

- Unit tests per grammar rule (lexer), per parse case (parser), per evaluation case (evaluator) — kept separate so a failure points at the right layer.
- Prefer testing the parser via the AST it produces, not by asserting on evaluated output — keeps parser tests from silently depending on evaluator correctness.

## Where the Reviewer Agent Fits

Each refactor step is small enough that the agent's review can focus on one thing: did this step change externally observable behavior of already-passing tests, and does the resulting code follow the conventions in [CLAUDE.md](/code-reviewer-agent/claude-md/).
