# Run Cockpit Foundation

Updated: 2026-05-18

This document records the Phase 57 return to normal product development after the Phase 56 readiness and CI closure work.

## Branch

```text
codex/phase-57-run-cockpit-operator-controls
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

## Boundaries

- No new production publishing flow.
- No login or permission UI.
- No WebSocket or SSE event stream.
- No replacement for the existing Conversations, Tasks, Playbooks, or Output Library pages.
- No new workflow execution semantics.
- No real OpenClaw or social media execution.
- No bulk action mode; every action is scoped to the selected run context.
- Navigation buttons switch pages only; they do not auto-select matching rows in the destination page yet.

## Acceptance

Local acceptance requires:

```powershell
npm run typecheck
npm run build
python scripts/verify_docs_runtime.py
python -m pytest -q
```

Remote acceptance requires the PR Quality Gates workflow to pass before merge.
