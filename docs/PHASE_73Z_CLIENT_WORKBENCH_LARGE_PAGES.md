# Phase 73Z Client Workbench Large Pages

## Scope

Phase 73Z keeps the Phase 73Y plan approval contract, but changes the customer-machine workbench information architecture so operators do not see planning, implementation, publishing, and diagnostics stacked in one long page.

- `worker_console` and `worker_console_desktop` now expose two large workbench pages: plan planning and plan implementation.
- New projects, draft projects, and reviewable plans default to the planning page, where the operator chooses the project, updates project knowledge, chats with the LLM, reviews the generated operation plan, regenerates if needed, and approves the plan.
- Approved projects automatically enter the implementation page. That page focuses on production tasks, ComfyUI workflow selection, output candidates, final selections, publish packages, and metric feedback.

## Implementation

- Both customer-machine frontends add `simpleWorkspacePage`, `activeSimpleWorkspacePage`, and `simpleWorkspaceImplementationReady`.
- The top project workspace adds `simple-workspace-page-tabs` so the operator can switch between the two large pages.
- The main panel carries `data-simple-workspace-page={activeSimpleWorkspacePage}`. CSS uses this attribute to hide implementation blocks on the planning page and hide the large planning chat on the implementation page.
- Approving an `OperationPlan` sets the workspace page to `implementation`; selecting a new project or submitting a new goal returns the workspace to `planning` until approval is available.

## Boundaries

This phase is frontend information architecture only. It does not auto-approve production tasks, submit ComfyUI prompts, mutate workflow JSON, run OpenClaw or Playwright, publish content, collect platform analytics, restart services, or bypass approval.

## Verification

- `tests/test_worker_console_client_ux.py` asserts that both customer-machine frontends expose the large page state, tabs, implementation page head, approval-to-implementation switch, and page-scoped CSS visibility rules.
- Real browser verification should confirm that `http://127.0.0.1:5181/` shows only the planning workspace until implementation is available, and that clicking the implementation tab hides the large planning chat while keeping project status visible.
