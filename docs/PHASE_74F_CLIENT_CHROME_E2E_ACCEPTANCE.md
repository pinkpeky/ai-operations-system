# Phase 74F Client Chrome E2E Acceptance

Date: 2026-06-03

## Objective

Phase 74F records the customer-machine Chrome acceptance pass for the strict operation-project workbench. The goal was to prove that the live web client is not only visually aligned with the reference template, but can complete the usable project loop through real browser clicks.

## Verified Scope

- Project creation with a fresh project title and theme.
- Current-project knowledge bootstrap when the project knowledge base is empty.
- LLM plan conversation, plan revision, and latest-plan-only approval.
- Copy task generation, full draft display, and copy approval.
- Automatic flow from approved copy into media production preparation.
- Workflow candidate selection and approval.
- Output candidate registration, selection, and publish package creation.
- Customer-machine publish dry-run through the local worker API.
- Operator-confirmed publish evidence recording.
- Publish result feedback, metric snapshot creation, and re-analysis.

## Implementation Notes

- `worker_console` and `worker_console_desktop` use the same project-loop implementation and local worker client contract.
- Vite dev and preview now proxy `/local-worker` to `http://127.0.0.1:9100`, which avoids browser CORS failures while keeping the local worker boundary explicit.
- The local worker client defaults to `/local-worker` instead of calling port `9100` directly from the browser.
- Publish dry-run remains a local worker diagnostic action.
- Final publish submission evidence is no longer treated as a real OpenClaw publish when the provider is mock. In the current customer-machine path, the UI records an explicit manual operator attestation and keeps the mock provider result as diagnostic context only.
- The implementation does not store platform credentials, bypass verification, click a real third-party final-submit button without operator control, run server-side account automation, mutate ComfyUI workflow JSON, or bypass approval gates.

## Chrome Acceptance Run

The acceptance run used the live Chrome page at `http://127.0.0.1:5184/` against the local API and worker services.

Fresh test project:

`验收测试 八项知识 KTV 1780432541711`

Observed successful browser-click sequence:

1. Created the project from the customer-machine UI.
2. Opened the project knowledge page and generated/uploaded 8 starter knowledge items for the project theme.
3. Generated operation plan v1 through the plan conversation.
4. Revised the plan to v2 through the conversation.
5. Approved only the latest plan version.
6. Generated the copy draft from the approved plan.
7. Opened the full copy body in the UI and approved the draft.
8. Confirmed the UI flowed into the media-production stage.
9. Selected and approved a workflow candidate.
10. Registered and selected an output preview.
11. Created a publish package.
12. Ran publish dry-run successfully through `/local-worker/openclaw/actions`.
13. Recorded operator-confirmed publish evidence.
14. Returned publish results and saw the page switch to data feedback.
15. Ran re-analysis and confirmed metric snapshots increased.

Final observed state:

- Current page: `数据回流`.
- Publish result message: `发布结果已回填，下一步可进行数据回流和再次分析。`
- Re-analysis message: `数据回流已登记，后端再次分析已完成。`
- Data feedback sidebar count increased.
- Re-analysis sidebar count increased.
- Metric snapshot panel showed 3 snapshots after the re-analysis step.

## Build Validation

Validated commands:

```powershell
npm.cmd run build
```

Validated workspaces:

- `worker_console`
- `worker_console_desktop`

Both builds completed successfully after the `/local-worker` proxy and publish evidence boundary updates.

## Remaining Boundary

The current acceptance proves the guarded customer-machine workflow and backend record chain. It does not prove a production OpenClaw provider that can perform a real platform publish action. A real provider still needs to be configured through the documented `openclaw_http` provider contract before non-manual final-submit automation can be considered production-ready.
