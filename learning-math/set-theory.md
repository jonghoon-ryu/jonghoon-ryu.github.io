---
layout: default
title: Set Theory
permalink: /learning-math/set-theory/
published: false
---
# Set Theory

Notes on the basics of set theory — the foundation most of math (and a good chunk of CS) is built on.

## What Is a Set

A set is an unordered collection of distinct elements. Written as `{1, 2, 3}` or defined by a rule: `{x | x is even}`. Two sets are equal if they contain exactly the same elements — order and duplicates don't matter.

## Basic Operations

- **Union** (`A ∪ B`) — elements in A, or B, or both
- **Intersection** (`A ∩ B`) — elements in both A and B
- **Difference** (`A − B`) — elements in A but not B
- **Complement** (`A′`) — elements not in A, relative to some universal set
- **Cartesian Product** (`A × B`) — all ordered pairs `(a, b)` with `a ∈ A`, `b ∈ B`

## Subsets and Power Sets

- `A ⊆ B` means every element of A is also in B.
- The **power set** `P(A)` is the set of all subsets of A, including the empty set and A itself. If `|A| = n`, then `|P(A)| = 2^n`.

## Russell's Paradox

Naive set theory allowed defining "the set of all sets that do not contain themselves." Asking whether this set contains itself leads to a contradiction either way — this broke naive set theory and motivated axiomatic set theory (ZFC), which restricts how sets can be formed to avoid this kind of self-reference.

## ZFC Axioms (Informally)

Zermelo-Fraenkel set theory with the Axiom of Choice — the standard foundation for modern math:

- **Extensionality** — sets with the same elements are equal
- **Pairing** — for any two sets, a set containing exactly those two exists
- **Union** — the union of a set of sets exists
- **Power Set** — the power set of any set exists
- **Infinity** — an infinite set exists (needed to construct the natural numbers)
- **Axiom of Choice** — given any collection of non-empty sets, it's possible to choose one element from each, even if there's no explicit rule for doing so

## Cardinality and Infinity

- Two sets have the same cardinality if there's a bijection (one-to-one correspondence) between them.
- **Countably infinite** sets (like the natural numbers ℕ) can be put in bijection with ℕ itself.
- **Cantor's diagonal argument** shows the real numbers ℝ are *uncountable* — a strictly larger infinity than ℕ. This was one of the most surprising results in 19th-century math.

## Relations and Functions as Sets

Everything reduces to sets: a **relation** between A and B is just a subset of `A × B`. A **function** `f: A → B` is a relation where every element of A maps to exactly one element of B. This is the formal foundation for how "functions" are defined rigorously in math (as opposed to informally, as a rule or formula).

## Why This Matters for CS

- Relational databases are literally built on set-theoretic relations (a table is a subset of a Cartesian product of column domains).
- Regular expressions and formal languages are defined as sets of strings, with union/intersection/complement operations mirroring set operations directly.
- Type theory and set theory both aim to formalize "collections of things," and comparing the two is a common way to understand why some programming languages pick one foundation over the other.
