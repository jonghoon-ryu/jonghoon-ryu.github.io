---
layout: default
title: Interpreter Kata
permalink: /code-reviewer-agent/interpreter/
---
# Interpreter Kata

The practice target for the code-reviewer-agent project: a small expression interpreter in C++, built deliberately without much upfront design so there's real structure to refactor later.

## Scope

A calculator-style interpreter that handles:

- Integer and floating-point literals
- Arithmetic operators (`+`, `-`, `*`, `/`) with standard precedence
- Parentheses for grouping
- Variable assignment and lookup

Deliberately out of scope for v1: functions, control flow, strings — enough is here already to have real refactoring targets (a growing `switch` in the evaluator, a parser that mixes tokenizing and parsing, etc.).

## Pipeline

1. **Lexer** — turns raw source text into a token stream (numbers, operators, identifiers, parens).
2. **Parser** — builds an expression tree (recursive descent, precedence climbing for `+ - * /`).
3. **Evaluator** — walks the tree and produces a value, using an environment map for variables.

## Why an Interpreter as a Review Target

- Small enough to hold in your head, large enough to have real design decisions (visitor pattern vs. switch-on-type, error handling for malformed input, where mutable state lives).
- Classic refactoring pressure points show up naturally: a parser that starts mixing concerns, an evaluator that grows a branch per new feature, error handling bolted on after the fact.
- Good fit for TDD — each grammar rule and evaluation case is independently testable.
