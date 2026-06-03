# Phase 74A Client Production Start Guide

Phase 74A follows Phase 73Z by making the implementation page actionable for operators who need to move from an approved operation plan into content production.

## Scope

- `worker_console` and `worker_console_desktop` now render `simple-production-guide` at the top of the implementation page.
- The guide exposes five ordered steps: import project material, approve production tasks, select a ComfyUI workflow, register content output, and confirm the selected output before publish preparation.
- The content-output step includes `simple-production-output-form`, so operators can enter a candidate title plus a file path, preview link, or copy text directly in the implementation page.
- The publish-preparation step can create a reviewable publish package from the server `package_blueprints` defaults, so the guide stays browser-testable without multiple prompt dialogs; approval is still required before any customer-machine execution.
- Each step calls the existing operator-click handlers, including `registerProjectMaterialFromClient`, `decideProjectTask`, `createManualWorkflowSelection`, `registerOutputCandidateFromClient`, `decideProjectOutputCandidate`, `decideProjectFinalSelection`, and `createPublishPackageFromClient`.
- Planning remains a separate large page; the guide is hidden while the worker is on the planning page and appears after an approved `OperationPlan` moves the project into implementation.
- Responsive styles keep the guide usable as a single-column sequence on smaller customer-machine screens.

## Operator Contract

Operators should be able to see where to start production without hunting through the detailed project record drawers. The production guide is an entry surface, not a replacement for the record sections. The detail drawers remain available for audit, review history, workflow candidates, output candidates, publish packages, and metric feedback.

## Non-Goals

Phase 74A does not auto-approve production tasks, upload files to ComfyUI, submit ComfyUI prompts, mutate workflow JSON, select output candidates without an operator click, create publish packages without an operator click, run OpenClaw, run Playwright, publish to social media, scrape analytics, restart services, or bypass approval.

## Verification

- Static contract coverage lives in `tests/test_worker_console_client_ux.py`.
- Documentation coverage lives in `tests/test_commercial_operations_docs.py`.
- Visible frontend changes must be validated in a real browser at the customer-machine console before they are treated as complete.
