---
layout: default
title: Outline
permalink: /code-reviewer-agent/outline/
---
# Outline

Plan for the code-reviewer-agent project: use an AI agent to review and drive incremental improvements on a small C++ codebase, practicing the fixes-and-reliability-improvements workflow from the course.

## Goals

- Build a small interpreter in C++ as a realistic, non-trivial review target.
- Configure an agent (via `CLAUDE.md`) with review conventions specific to this project.
- Practice a refactor → test → review loop rather than one-shot code generation.
- Compare agent-suggested fixes against manual review to see where the agent helps and where it misses things.

## Phases

1. **Baseline** — get a minimal interpreter working (lexer → parser → evaluator) with no tests, to have something worth reviewing.
2. **Add tests first** — backfill unit tests before touching structure, so refactors are ever a regression against something.
3. **Refactor with TDD** — apply small, test-covered refactoring steps (see [C++ Refactoring & TDD](/code-reviewer-agent/cpp-refactoring-tdd/)).
4. **Agent-assisted review** — have the agent review each change for correctness, readability, and reliability issues; compare against the [outline of agent instructions](/code-reviewer-agent/claude-md/).
5. **Retrospective** — note where the agent's review caught real issues vs. false positives.

## Open Questions

- How much project-specific context does the agent need in `CLAUDE.md` before its reviews stop being generic?
- Where's the right boundary between "agent flags it" and "agent fixes it automatically"?
