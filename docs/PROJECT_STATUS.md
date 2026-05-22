# Project Status

## Branch Status

`main` is the Phase 55 stable baseline after PR #17 merged the Phase 43-55 Combined Release Candidate and after post-merge stabilization landed. PR #3-#14 are marked merged after PR #17 because their changes are contained in `main`; PR #1 and PR #15 are closed as superseded after verification. PR #16 was accepted into the Phase 54 branch before PR #17 merged to `main`. Phase 56 was reverted and is not active. Phase 56A-56D readiness work has landed on `main`, adding CI gates, required-check documentation, release readiness artifacts, and scheduled server Docker smoke. Phase 57A-57D, Phase 58A-58E, Phase 59A-59C, Phase 60A-60G, and Phase 61A-61P have also landed on `main`, adding the Admin Dashboard Run Cockpit, guarded cockpit actions, operator controls, deep links, refresh UX, Playbooks context, Output Library context handoff, Phase 58 closeout, Run Cockpit search density, workflow handoff, workflow focus/provenance, the frontend language foundation, the Overview role entry, the Conversations operator console, the RAG Documents knowledge console, RAG knowledge maintenance controls, Replay Center workflow observability simplification, RAG live validation guidance, the Commercial Ops project center, commercial operation evidence/handoff links, commercial operation approval gates, commercial operation safe dry-runs, commercial operation content drafts, commercial operation asset requests, commercial operation deliverables, commercial operation execution requests, commercial operation execution runs, commercial operation results, commercial operation monitoring observations, commercial operation optimization decisions, commercial operation evidence snapshots, commercial operation RAG evidence generation, commercial operation RAG content draft generation, and commercial operation RAG asset brief generation.

## Localized Status Docs

- English: `docs/en/PROJECT_STATUS.md`
- Chinese: `docs/zh/PROJECT_STATUS.md`

## Notes

Use `docs/PHASE_INDEX.md` as the complete phase index and `docs/CURRENT_NEXT_PHASE.md` as the next-conversation recovery state file.

## Active Next Slice

`codex/phase-62i-workstation-client-ux` is the active next branch and PR #75 is open as a draft. It adds Phase 62I Workstation/Customer Client Frontend UX Alignment after PR #74 / Phase 62H ComfyUI Runtime Post-Manual Readiness Checks from `codex/phase-62h-comfyui-post-manual-readiness` and its `/api/v1/comfyui-runtime/health` recovery surface: `worker_console` and `worker_console_desktop` now expose a clearer customer-machine operator home, simple local connection/runtime/heartbeat/recovery status cards, runtime and heartbeat controls, conversation/playbook/task/output shortcuts, approval queue visibility, failure recovery guidance, setup/help panels, Chinese/English language switching, and explicit server-vs-customer-machine boundary warnings. This phase remains a frontend/readiness slice and does not add ComfyUI calls, OpenClaw execution, platform publishing, account control, installer signing, auto-update, captcha bypass, proxy pools, fingerprint bypass, secret resolution, or approval bypass. The guarded `GET /system_stats` ComfyUI health probe remains gated by the existing provider/enabled/network/host/path/read-only controls.

Phase 62H remains the immediate runtime readiness predecessor for this slice: `/api/v1/comfyui-runtime/health`, `/api/v1/comfyui-runtime/capabilities`, `/api/v1/comfyui-runtime/diagnostics`, `/api/v1/comfyui-runtime/maintenance-runbook`, `/api/v1/comfyui-runtime/config-change-requests`, `/api/v1/comfyui-runtime/manual-apply-evidence`, `/api/v1/comfyui-runtime/post-manual-readiness-checks`, and `/api/v1/comfyui-runtime/diagnostic-snapshots` stay visible through the Admin Dashboard ComfyUI page with `manual_config_applied`, `api_config_mutation_performed`, `guarded_probe_ready`, and `health_probe_executed` metadata only.
