# Project Status

## Branch Status

`main` is the Phase 55 stable baseline after PR #17 merged the Phase 43-55 Combined Release Candidate and after post-merge stabilization landed. PR #3-#14 are marked merged after PR #17 because their changes are contained in `main`; PR #1 and PR #15 are closed as superseded after verification. PR #16 was accepted into the Phase 54 branch before PR #17 merged to `main`. Phase 56 was reverted and is not active. Phase 56A-56D readiness work has landed on `main`, adding CI gates, required-check documentation, release readiness artifacts, and scheduled server Docker smoke. Phase 57A-57D, Phase 58A-58E, Phase 59A-59C, Phase 60A-60G, and Phase 61A-61P have also landed on `main`, adding the Admin Dashboard Run Cockpit, guarded cockpit actions, operator controls, deep links, refresh UX, Playbooks context, Output Library context handoff, Phase 58 closeout, Run Cockpit search density, workflow handoff, workflow focus/provenance, the frontend language foundation, the Overview role entry, the Conversations operator console, the RAG Documents knowledge console, RAG knowledge maintenance controls, Replay Center workflow observability simplification, RAG live validation guidance, the Commercial Ops project center, commercial operation evidence/handoff links, commercial operation approval gates, commercial operation safe dry-runs, commercial operation content drafts, commercial operation asset requests, commercial operation deliverables, commercial operation execution requests, commercial operation execution runs, commercial operation results, commercial operation monitoring observations, commercial operation optimization decisions, commercial operation evidence snapshots, commercial operation RAG evidence generation, commercial operation RAG content draft generation, and commercial operation RAG asset brief generation.

## Localized Status Docs

- English: `docs/en/PROJECT_STATUS.md`
- Chinese: `docs/zh/PROJECT_STATUS.md`

## Notes

Use `docs/PHASE_INDEX.md` as the complete phase index and `docs/CURRENT_NEXT_PHASE.md` as the next-conversation recovery state file.

## Active Next Slice

`codex/phase-62m-client-goal-templates` is the active next branch after PR #78 / Phase 62L Customer Console Task Workbench. It adds Phase 62M Customer Console Goal Templates: `worker_console` and `worker_console_desktop` now expose standard launch content, RAG evidence, asset brief, and page report templates in the first customer-machine task workbench. Selecting a template preloads the operating goal and recommended playbook while preserving local runtime/heartbeat controls, Chinese/English language switching, approvals, playbooks, outputs, tasks, logs, and server-vs-customer-machine boundary warnings. It does not import ComfyUI adapters, call ComfyUI, submit prompts, read or submit queues, upload files, generate media, enable runtime switches, write environment variables, restart services, mutate runtime configuration, resolve secrets, publish, run OpenClaw, control accounts, or bypass approval.

The active runtime surface includes `/api/v1/comfyui-runtime/health`, `/api/v1/comfyui-runtime/capabilities`, `/api/v1/comfyui-runtime/diagnostics`, `/api/v1/comfyui-runtime/maintenance-runbook`, `/api/v1/comfyui-runtime/config-change-requests`, `/api/v1/comfyui-runtime/manual-apply-evidence`, `/api/v1/comfyui-runtime/post-manual-readiness-checks`, `/api/v1/comfyui-runtime/guarded-probe-executions`, and `/api/v1/comfyui-runtime/diagnostic-snapshots`, with `api_config_mutation_performed=false`, `guarded_probe_ready`, `health_probe_executed`, `external_request_attempted`, and `probe_result_status` audit fields.

Phase 62L Customer Console Task Workbench from `codex/phase-62l-client-task-workbench` remains the immediate customer-console UX predecessor for this slice. Phase 62K Customer Console Codex-like UX Simplification from `codex/phase-62k-customer-console-codex-ux` remains the earlier simplification predecessor, and Phase 62J remains the immediate runtime predecessor: the server-side ComfyUI guarded probe audit is approval-gated, while Phase 62M keeps the customer-machine UI focused on template-assisted goal submission, approval handling, and task recovery before exposing dense maintenance internals.

Phase 62I Workstation/Customer Client Frontend UX Alignment from `codex/phase-62i-workstation-client-ux` remains the earlier customer-console baseline for `worker_console` and `worker_console_desktop`, including Chinese/English language switching, local runtime/heartbeat visibility, and server-vs-customer-machine boundary guidance.

Phase 62J still depends on Phase 62H ComfyUI Runtime Post-Manual Readiness Checks for the approved guarded read-only probe chain; Phase 62M does not loosen that runtime boundary.
