# Phase 73U Client Visual Approval Workbench

Phase 73U aligns the customer-machine workbench with the clarified operator flow: a staff member enters an operating goal, then reviews the operation plan, ComfyUI image/video results, workflow selection, and RAG knowledge updates from one simple visual approval surface.

## Runtime Changes

- `worker_console/src/main.tsx` and `worker_console_desktop/src/main.tsx` derive `simpleApprovalDeskPlan`, `simpleApprovalDeskWorkflow`, `simpleApprovalDeskOutputCandidates`, and approval-state values from the existing project workbench records.
- Both customer-machine consoles render `simple-approval-workbench` immediately after `simple-goal-box`, so the first screen is goal input, visual approval, current work, and then folded production detail.
- The visual approval workbench has four cards: operation plan, ComfyUI image/video output candidates, workflow selection, and RAG knowledge.
- Image, video, and audio candidates render directly in `simple-approval-output-preview` when a preview URI is available; unknown artifact types remain visible as packaged output records.
- Plan, workflow, and output buttons reuse the existing explicit operator-click handlers: `decideProjectPlan`, `decideProjectWorkflowSelection`, `decideProjectOutputCandidate`, `openClientProjectRecordsAndScroll`, and `onOpenKnowledge`.
- `worker_console/src/styles.css` and `worker_console_desktop/src/styles.css` add the `simple-approval-workbench` layout, status styles, media previews, compact action rows, and responsive single-column behavior.

## Boundary

Phase 73U is frontend information architecture and visual approval surfacing only. It does not create operations automatically, does not approve records without an operator click, does not reject records without an operator click, does not select output candidates without an operator click, does not submit ComfyUI prompts, does not mutate workflow JSON, does not overwrite original workflow files, does not run OpenClaw actions, does not run Playwright, does not publish, does not click final submit, does not collect credentials, does not ingest analytics, does not restart services automatically, and does not bypass approval.
