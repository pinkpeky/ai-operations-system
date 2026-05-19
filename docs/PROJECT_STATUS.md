# Project Status

## Branch Status

`main` is the Phase 55 stable baseline after PR #17 merged the Phase 43-55 Combined Release Candidate and after post-merge stabilization landed. PR #3-#14 are marked merged after PR #17 because their changes are contained in `main`; PR #1 and PR #15 are closed as superseded after verification. PR #16 was accepted into the Phase 54 branch before PR #17 merged to `main`. Phase 56 was reverted and is not active. Phase 56A-56D readiness work has landed on `main`, adding CI gates, required-check documentation, release readiness artifacts, and scheduled server Docker smoke. Phase 57A-57D, Phase 58A-58E, and Phase 59A have also landed on `main`, adding the Admin Dashboard Run Cockpit, guarded cockpit actions, operator controls, deep links, refresh UX, Playbooks context, Output Library context handoff, Phase 58 closeout, and Run Cockpit search density.

## Localized Status Docs

- English: `docs/en/PROJECT_STATUS.md`
- Chinese: `docs/zh/PROJECT_STATUS.md`

## Notes

Use `docs/PHASE_INDEX.md` as the complete phase index and `docs/CURRENT_NEXT_PHASE.md` as the next-conversation recovery state file.

## Active Next Slice

`codex/phase-59-run-cockpit-workflow-handoff` is the active next branch. It carries Run Cockpit `workflow_run_id` context into Workflows and Replay Center, displays linked workflow/runtime summary context, and preserves existing workflow execution boundaries. It does not reuse the reverted Phase 56 branch.
