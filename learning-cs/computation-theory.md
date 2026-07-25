---
layout: default
title: Computation Theory
permalink: /learning-cs/computation-theory/
---
# Computation Theory

Notes on the theory of computation — what can be computed, and how efficiently.

## Automata Hierarchy (Chomsky Hierarchy)

From least to most powerful:

1. **Finite Automata (FA)** — recognize regular languages (e.g. `a*b+`). No memory beyond current state.
2. **Pushdown Automata (PDA)** — recognize context-free languages, using a stack for memory (e.g. matching balanced parentheses).
3. **Linear Bounded Automata (LBA)** — recognize context-sensitive languages.
4. **Turing Machines (TM)** — recognize recursively enumerable languages; the most general model of computation.

## The Turing Machine

A Turing machine is an infinite tape, a read/write head, and a finite set of states with transition rules. Despite its simplicity, it's believed to capture everything "computable" — this is the **Church-Turing thesis**: any function computable by an effective procedure is computable by a Turing machine.

## Decidability

A problem is **decidable** if a Turing machine exists that halts on every input with the correct yes/no answer.

- **Halting Problem**: given a program and input, does it halt? Proven **undecidable** by Turing (1936) via a diagonalization argument — no algorithm can solve this for all programs.
- This result underlies why general-purpose static analysis (e.g. "does this code ever crash?") can't be fully automated for all programs.

## Complexity Classes

- **P** — problems solvable in polynomial time (efficiently solvable)
- **NP** — problems whose solutions can be *verified* in polynomial time (not necessarily found quickly)
- **NP-complete** — the hardest problems in NP; if any one has a polynomial-time solution, then P = NP (e.g. SAT, Traveling Salesman, Subset Sum)
- **P vs NP** — one of the most famous open problems in computer science: is every problem whose solution can be verified quickly also solvable quickly?

## Reductions

A key proof technique: to show problem B is at least as hard as problem A, reduce A to B — i.e., show any instance of A can be transformed (in polynomial time) into an instance of B. This is how NP-completeness proofs chain together, all tracing back to the original NP-complete problem, SAT (Cook-Levin theorem).

## Why It Matters Practically

- Recognizing a problem is NP-complete tells you to stop searching for an efficient exact algorithm and instead consider approximations, heuristics, or restricting the problem's scope.
- Regular expressions are literally finite automata — understanding their limits (can't match balanced parens) comes directly from the Chomsky hierarchy.
- Compilers use pushdown automata concepts (via context-free grammars) to parse programming language syntax.

## Further Reading

- *Introduction to the Theory of Computation* by Michael Sipser — the standard textbook
- Computerphile's Turing Machine and Halting Problem videos — good visual intuition
