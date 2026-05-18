# Run Cockpit Foundation

Updated: 2026-05-18

This document records the Phase 57 return to normal product development after the Phase 56 readiness and CI closure work.

## Branch

```text
codex/phase-57-run-cockpit-foundation
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

## User Outcome

An operator can open one screen and answer:

- Which conversation or background task is active.
- Whether a selected thread needs human approval.
- Which task run has failed or can be recovered.
- Which artifacts were produced by the selected run context.
- What the latest thread event or task event says.

## Boundaries

- No new production publishing flow.
- No login or permission UI.
- No WebSocket or SSE event stream.
- No replacement for the existing Conversations, Tasks, Playbooks, or Output Library pages.
- No new workflow execution semantics.
- No real OpenClaw or social media execution.

## Acceptance

Local acceptance requires:

```powershell
npm run typecheck
npm run build
python scripts/verify_docs_runtime.py
python -m pytest -q
```

Remote acceptance requires the PR Quality Gates workflow to pass before merge.
