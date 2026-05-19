# Run Cockpit Foundation

Updated: 2026-05-19

This document records the Phase 57 return to normal product development after the Phase 56 readiness and CI closure work.

## Branch

```text
codex/phase-58-output-library-context
```

## Scope

Phase 57 adds an Admin Dashboard `Run Cockpit` page that correlates existing runtime surfaces:

- Conversation threads.
- Background task runs.
- Pending approvals for the selected thread.
- Playbook runs.
- Output artifacts linked to the selected thread or task run.
- Task run events and diagnostics.
- Scheduler health.

The page is a frontend composition layer over existing APIs. It does not introduce a new backend aggregate model.

The current action slice adds guarded operations directly inside the cockpit detail panel:

- Approve, reject, cancel, or execute a selected thread approval.
- Retry, cancel, resume, or recover a selected task run.
- Export linked artifacts as markdown or JSON.
- Show a compact last-action result preview after an operation.

The current operator-controls slice adds:

- Task view filters for active, attention, and all task runs.
- Optional auto refresh using the dashboard refresh interval.
- Navigation buttons from the cockpit detail panel to Conversations, Playbooks, Tasks, and Output Library.

The current closeout slice records Phase 57 status after PR #24:

- Phase 57A, 57B, and 57C are merged to `main`.
- Phase 57D reconciles status docs so the completed 57C branch is no longer listed as active.
- A lightweight test guards the phase index against leaving merged run cockpit slices as `TBD` or `In progress`.

The current deep-link slice adds:

- URL query state for the active Admin Dashboard page.
- Run Cockpit handoff links with `thread_id`, `task_run_id`, and `artifact_id`.
- Specialist pages that open the linked Conversation, Task Run, or Output Artifact detail directly.

The current refresh-UX slice adds:

- Auto-refresh state labels in the Run Cockpit summary strip.
- Refresh interval and next-refresh countdown labels.
- Stale-data preservation when a cockpit refresh fails after prior data loaded.

The current playbook-context slice adds:

- Playbooks page awareness of `thread_id` deep-link context.
- Filtered Playbook Runs when opened from a selected Run Cockpit thread.
- Controls to open the linked Conversation or clear the Playbooks thread context.

The current output-library-context slice adds:

- Output Library awareness of `thread_id`, `task_run_id`, and `artifact_id` deep-link context.
- Filtered artifact lists when opened from a selected Run Cockpit thread or task.
- Controls to open the linked Conversation, open the linked Task Run, or clear the Output Library context.

## User Outcome

An operator can open one screen and answer:

- Which conversation or background task is active.
- Whether a selected thread needs human approval.
- Which task run has failed or can be recovered.
- Which artifacts were produced by the selected run context.
- What the latest thread event or task event says.
- Whether the most common approval, task, or artifact action succeeded.
- Which task runs need attention without leaving the cockpit.
- Where to continue deeper inspection in the existing specialist pages.
- A shareable URL for the selected specialist page context after leaving the cockpit.
- Whether cockpit data is idle, refreshing, or stale without losing the previous scan result.
- A Playbooks page that stays scoped to the selected cockpit thread until the operator clears that context.
- An Output Library page that stays scoped to the selected cockpit thread/task/artifact until the operator clears that context.

## Boundaries

- No new production publishing flow.
- No login or permission UI.
- No WebSocket or SSE event stream.
- No replacement for the existing Conversations, Tasks, Playbooks, or Output Library pages.
- No new workflow execution semantics.
- No real OpenClaw or social media execution.
- No bulk action mode; every action is scoped to the selected run context.
- Deep links do not add authentication, permissions, or share-token semantics; they only restore local dashboard page context.
- Auto refresh remains polling-based; no WebSocket or SSE stream is introduced.
- Playbooks filtering is local to the Admin Dashboard list; it does not add new backend query semantics.
- Output Library context filtering is local to the Admin Dashboard list; it does not add new backend query semantics.

## Acceptance

Local acceptance requires:

```powershell
npm run typecheck
npm run build
python scripts/verify_docs_runtime.py
python -m pytest -q
```

Remote acceptance requires the PR Quality Gates workflow to pass before merge.
