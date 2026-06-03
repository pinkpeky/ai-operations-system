# Phase 68G Publish Package Preparation

Date: 2026-05-30

## Goal

Phase 68G connects approved final outputs to platform-specific publish package drafts.

The operator workflow is:

1. Staff preview generated output and approve a `FinalSelection`.
2. The customer-machine frontend asks the server for a `publish-prep-package`.
3. The server checks whether the final selection and selected output are ready for packaging.
4. The server returns editable platform copy blueprints, platform policy, review gates, and existing `PublishPackage` records.
5. The operator edits title, body, hashtags, and account reference.
6. The server creates a `PublishPackage` and moves it to `ready_for_review`.
7. Human operator approval is still required before customer-machine execution or metric collection.

This phase does not run OpenClaw, run Playwright, publish to social platforms, control accounts, mutate ComfyUI workflows, submit prompts, generate assets, bypass operator approval, restart services, or mutate runtime configuration.

## Implemented Scope

- `GET /api/v1/commercial-operations/{operation_id}/final-selections/{final_selection_id}/publish-prep-package`
- `CommercialOperationPublishPrepPackage`
- `CommercialOperationService.get_publish_prep_package()`
- Readiness checks for approved `FinalSelection` and selected `OutputCandidate`
- Platform targets, platform policy, copy guidance, review gates, and publish package blueprints
- Customer-machine `createPublishPackage` and `getPublishPrepPackage` client methods
- `Phase 68G Publish Package Preparation` panel in `worker_console/src/main.tsx`
- Matching desktop panel in `worker_console_desktop/src/main.tsx`
- `tests/test_operation_project_governance.py`
- `tests/test_worker_console_client_ux.py`

## Publish Prep Package

The `publish-prep-package` endpoint is read-only.

It returns:

- final selection id and status;
- selected output candidate details;
- readiness status and blocking reasons;
- platform targets from `FinalSelection.platform_targets`, operation channels, or a manual-review fallback;
- platform policy for social copy length, hashtag count, account confirmation, and metric pull targets;
- editable `PublishPackage` blueprints;
- existing publish packages tied to the final selection;
- review gates for approval and later customer-machine execution.

## Customer-Machine Behavior

The customer-machine workbench now exposes a publish preparation action once a final selection is approved and no active publish package already exists for it.

Operators can:

- refresh publish readiness;
- edit platform, title, body, hashtags, and account reference;
- create a `PublishPackage`;
- move that package to `ready_for_review`;
- keep approval separate from execution.

This is intentionally not a one-click publish flow. Publishing through OpenClaw and Playwright remains a later explicit execution contract.

## Review Boundary

`PublishPackage` creation is not publishing.

The required gates remain:

- `FinalSelection` must be approved;
- the linked `OutputCandidate` must remain selected;
- platform copy must be reviewed by staff;
- `PublishPackage` must be approved before customer-machine execution;
- OpenClaw/Playwright execution requires a separate handoff;
- platform metrics must be returned after publish for closed-loop analysis.

## Project Fit

Phase 68G is project-wide. It can prepare packages for Douyin, TikTok, Xiaohongshu, WeChat, Instagram-style channels, or manual review channels.

KTV short video is one supported project type, not the only target. The same contract works for image posts, video posts, audio-led posts, copy posts, and future platform-specific adapters.

## Verification

- Backend syntax compile must pass for service, schemas, and routes.
- `tests/test_operation_project_governance.py` must verify the `publish-prep-package` contract.
- `tests/test_worker_console_client_ux.py` must verify web/desktop client methods, frontend state, panel classes, and documentation.
- Web and Desktop typecheck/build must pass.

## Next Step

The next project slice should define the customer-machine publish execution handoff: an approved `PublishPackage` becomes a guarded client task for OpenClaw/Playwright, with clear account confirmation, dry-run evidence, execution logs, and metric pullback boundaries.
