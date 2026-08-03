---
layout: default
title: Agent Instructions (CLAUDE.md)
permalink: /code-reviewer-agent/claude-md/
---
# Agent Instructions (CLAUDE.md)

The project-specific `CLAUDE.md` used to configure the reviewer agent for the [interpreter kata](/code-reviewer-agent/interpreter/) codebase, and the reasoning behind each section.

## What Goes In It

- **Build/test commands** — how to compile and run the interpreter's test suite, so the agent can verify a refactor didn't break anything before commenting on style.
- **Review priorities, in order** — correctness first (does it still evaluate the same test cases), then memory safety (no raw owning pointers, no leaks introduced), then readability, then style.
- **Refactoring conventions specific to this project** — e.g. "prefer a visitor over a growing switch once a node type gets a fourth case," matching the moves in [C++ Refactoring & TDD](/code-reviewer-agent/cpp-refactoring-tdd/).
- **Things not to flag** — deliberately simple/minimal v1 code (see the interpreter's scope) that's simple on purpose, not by oversight, so the agent doesn't push premature abstraction.

## Why a Project-Specific File Instead of Generic Instructions

A generic "review this C++ code" prompt tends to produce generic feedback — naming nits, boilerplate suggestions. Pointing the agent at this project's actual TDD workflow and refactoring conventions makes its review comparable to a teammate who's read the [outline](/code-reviewer-agent/outline/): it knows which step of red-green-refactor a given diff is in, and reviews accordingly instead of asking for tests that already exist elsewhere in the cycle.

## Retro Notes

Fill in here as the project progresses — where the agent's review matched a human reviewer's judgment, and where the `CLAUDE.md` needed a follow-up rule to stop a repeated false positive.
