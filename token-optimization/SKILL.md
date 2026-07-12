---
name: token-optimization
description: Minimize Claude Code token and context usage while preserving correctness. Use when the user requests efficient execution, lower usage, narrow codebase exploration, or concise implementation.
argument-hint: [task or scope]
---

# Token-optimized execution

Apply these rules to `$ARGUMENTS`. If no argument is supplied, apply them to the current user request.

## Objective

Complete the task correctly using the smallest necessary amount of context, tool output, reasoning effort, and response text.

## Workflow

### 1. Lock the scope

* Identify the exact deliverable, probable files, constraints, and acceptance check.
* Do not investigate unrelated architecture or improve unrelated code.
* Ask a question only when missing information blocks safe execution. Otherwise use the smallest reversible assumption.
* For a simple task, act immediately. Create a short plan only for genuinely multi-step or risky work.

### 2. Read narrowly

* Start with existing conversation context, `git status`, `git diff`, manifests, and known entry points when relevant.
* Prefer Glob, Grep, symbol navigation, and targeted searches before reading files.
* Read only relevant files and line ranges. Do not read a whole large file when a section is sufficient.
* Do not reread unchanged files or repeat output already available in context.
* Ignore generated files, lockfiles, build artifacts, minified files, dependencies, caches, and large logs unless directly required.
* Filter large command output before it reaches the conversation. Prefer focused flags, `grep`, `head`, `tail`, or a small script that returns only relevant lines.

### 3. Execute efficiently

* Batch independent searches, reads, and checks when possible.
* Make the smallest safe patch that satisfies the request.
* Preserve existing project patterns instead of inventing new abstractions.
* Avoid speculative refactors, duplicate implementations, unnecessary comments, extra documentation, and unrelated formatting.
* Do not use an agent team for ordinary work.
* Use one isolated Explore subagent only when broad investigation would otherwise flood the main context. Require a concise summary with file paths and line references.
* Use the lowest reasoning effort adequate for the task. Escalate only for architecture, security, unclear failures, or genuinely difficult decisions.

### 4. Verify proportionally

* Run the narrowest relevant test, type check, lint command, build step, or visual check.
* Expand verification only when the change is cross-cutting, the targeted check fails, or the user explicitly requests full verification.
* Keep output compact: show failures, essential diagnostics, and the final pass result rather than full successful logs.
* Do not rerun a command unless code, configuration, dependencies, or relevant state changed.
* Stop when the acceptance criteria are satisfied.

### 5. Communicate compactly

* Do not narrate routine file reads, searches, or obvious implementation steps.
* During work, report only meaningful findings, decisions, risks, or blockers.
* Do not paste complete files or unchanged code unless explicitly requested.
* Final response format:

  1. Result
  2. Files changed
  3. Verification
  4. One caveat or next action only when necessary
* Keep the final response concise and avoid repeating the user’s request.

## Context hygiene

* Treat context as a limited resource.

* Reuse information already present instead of rediscovering it.

* When unrelated history is dominating the session, recommend `/clear`.

* When the current task must continue but context is becoming crowded, recommend one focused command such as:

  `/compact focus on the current task, decisions, changed files, failures, and verification results`

* Recommend a context command at most once unless the user asks again.

## Avoid these waste patterns

* Scanning the entire repository before locating the likely target.
* Reading every file in a directory “for completeness.”
* Running full test suites before a targeted check.
* Repeating `git status`, searches, builds, or tests without a state change.
* Launching multiple agents for a small task.
* Loading unused MCP tools or external documentation.
* Returning long explanations, exhaustive logs, or large code dumps by default.
* Continuing after the requested result is already verified.

## Completion check

Before responding, silently confirm:

* The requested scope is complete.
* No unrelated files were changed.
* Verification is sufficient for the risk.
* The response contains no unnecessary detail.
