---
layout: default
title: bbchallenge — Busy Beaver notes
permalink: /open-problems/busy-beaver/bbchallenge-notes/
---
# bbchallenge — Busy Beaver notes

<p class="post-meta">September 26, 2026</p>

## What it is

The **Busy Beaver Challenge** (bbchallenge) is an online collaboration, mostly of hobbyists and programmers, working on one of the purest problems in computer science.

**The problem.** Take a tiny Turing machine. It has *n* internal states, an infinite tape of 0s and 1s, and a small rule table that says what to write, which way to move and which state to go to next. Started on a blank tape, most machines either halt quickly or run forever. **BB(n)** is the longest any *n*-state machine can run before halting, not counting machines that never halt.

- BB(1)=1, BB(2)=6, BB(3)=21, BB(4)=107 were settled decades ago.
- **BB(5) = 47,176,870** was open from the 1960s until **2024**, when bbchallenge settled it.

## Why it's hard, and how BB(5) fell

To prove BB(5), you must show that every one of the roughly 180 million 5-state machines either halts within 47,176,870 steps or provably never halts. There's no general algorithm for that; it's the halting problem.

The community wrote **deciders**, programs that each recognize one kind of non-halting behavior: loops, counters, cyclers, translated cyclers, and so on. They ran them over all the machines, then attacked the stubborn holdouts one at a time. The final proof was machine-checked in **Coq**.

## The open frontier

- **BB(6)** is unknown. 6-state champions have been found that run for more than 2↑↑↑5 steps, a number far too large to write out in ordinary notation.
- **Antihydra** and similar "cryptids" are unresolved 6-state machines that behave like Collatz-type iterations. Deciding whether they halt would mean solving a Collatz-like open problem.

## Why it fits me, and how to start

This is systems work: enumerating machines, simulating them fast, writing deciders and verifying proofs. Most contributors were amateurs who coordinated online and got credit on a real result.

1. Read **The Story** on bbchallenge.org, a readable account of how BB(5) fell.
2. Browse the wiki's **BB(6)** page for the current frontier and the list of holdout machines.
3. Write my own Turing machine simulator and a simple loop decider, a weekend project.

## Other open problems to look at

- **Brocard's problem:** n! + 1 = m². The only known solutions are n = 4, 5, 7.
- **Erdős–Moser equation:** 1ᵏ + … + (m−1)ᵏ = mᵏ. The only known solution is 1 + 2 = 3.
- **Magic square of squares:** 3×3, with nine distinct perfect squares. Still open.
- **Perfect cuboid:** a box where every edge and diagonal is an integer. None found.
- **Sierpiński problem:** is 78557 the smallest Sierpiński number? PrimeGrid is working through the remaining candidates.
- **Happy Ending problem:** the case n = 7 is open, a good target for SAT solvers.
- **Graceful Tree conjecture**, **No-three-in-line**, **Van der Waerden numbers**.

## Sources

- [The Busy Beaver Challenge](https://bbchallenge.org/)
- [The Busy Beaver Challenge Story](https://bbchallenge.org/story)
- [BB(6) – BusyBeaverWiki](https://wiki.bbchallenge.org/wiki/BB%286%29)
- [Quanta: Busy Beaver Hunters Reach Numbers That Overwhelm Ordinary Math](https://www.quantamagazine.org/busy-beaver-hunters-reach-numbers-that-overwhelm-ordinary-math-20250822/)
- [Why Busy Beaver Hunters Fear the Antihydra](https://benbrubaker.com/why-busy-beaver-hunters-fear-the-antihydra/)
- [bbchallenge on GitHub](https://github.com/bbchallenge)
