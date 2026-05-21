# Project Status

## Branch Status

`main` is the Phase 55 stable baseline after PR #17 merged the Phase 43-55 Combined Release Candidate and after post-merge stabilization landed. PR #3-#14 are marked merged after PR #17 because their changes are contained in `main`; PR #1 and PR #15 are closed as superseded after verification. PR #16 was accepted into the Phase 54 branch before PR #17 merged to `main`. Phase 56 was reverted and is not active. Phase 56A-56D readiness work has landed on `main`, adding CI gates, required-check documentation, release readiness artifacts, and scheduled server Docker smoke. Phase 57A-57D, Phase 58A-58E, Phase 59A-59C, Phase 60A-60G, and Phase 61A-61P have also landed on `main`, adding the Admin Dashboard Run Cockpit, guarded cockpit actions, operator controls, deep links, refresh UX, Playbooks context, Output Library context handoff, Phase 58 closeout, Run Cockpit search density, workflow handoff, workflow focus/provenance, the frontend language foundation, the Overview role entry, the Conversations operator console, the RAG Documents knowledge console, RAG knowledge maintenance controls, Replay Center workflow observability simplification, RAG live validation guidance, the Commercial Ops project center, commercial operation evidence/handoff links, commercial operation approval gates, commercial operation safe dry-runs, commercial operation content drafts, commercial operation asset requests, commercial operation deliverables, commercial operation execution requests, commercial operation execution runs, commercial operation results, commercial operation monitoring observations, commercial operation optimization decisions, commercial operation evidence snapshots, commercial operation RAG evidence generation, commercial operation RAG content draft generation, and commercial operation RAG asset brief generation.

## Localized Status Docs

- English: `docs/en/PROJECT_STATUS.md`
- Chinese: `docs/zh/PROJECT_STATUS.md`

## Notes

Use `docs/PHASE_INDEX.md` as the complete phase index and `docs/CURRENT_NEXT_PHASE.md` as the next-conversation recovery state file.

## Active Next Slice

`codex/phase-62b-comfyui-guarded-readonly-probe` is the active next branch. It adds Phase 62B ComfyUI Guarded Read-Only Probe on top of the Phase 62A contract: `/api/v1/comfyui-runtime/health`, `/api/v1/comfyui-runtime/capabilities`, `ComfyUIRuntimeService`, `COMFYUI_RUNTIME_READ_ONLY_PROBE_ENABLED`, `COMFYUI_RUNTIME_HEALTH_PATH`, `COMFYUI_RUNTIME_ALLOWED_HEALTH_PATHS`, Docker environment exposure, docs/runtime verification, and a dedicated Admin Dashboard ComfyUI tab probe panel for provider, switch, base URL, host/path allowlists, probe status, and latency visibility. The default still does not attempt network calls. The only allowed live request is `GET /system_stats` when every explicit gate is enabled; it still does not upload or ingest knowledge files, store or resolve secret values, enable runtime switches, mutate runtime configuration, auto-approve assets, auto-publish, execute external actions, run Browser Worker actions, run OpenClaw actions, import or call ComfyUI adapters, call ComfyUI execution endpoints, read ComfyUI queues, upload files to ComfyUI, submit ComfyUI jobs, generate media, control real accounts, ingest platform analytics, claim ROI attribution, or bypass approval.
