# Phase 73V Client Project Conversation Workspace

Phase 73V restructures the customer-machine first screen around the clarified plan-first operator flow. The worker chooses an existing/current project or starts a new project draft, then uses one large chat workspace to talk with the LLM, update RAG context, generate the overall operation plan, regenerate it when unsatisfactory, and complete manual approval before moving to production outputs.

Follow-up: Phase 73W fixes the real-page empty-project and plan-detail gaps found after Phase 73V. All-project deletion must now leave a stable empty picker with no stale selected operation, and the plan card must show structured strategy fields instead of only the objective summary.

## Runtime Changes

- `worker_console` and `worker_console_desktop` now keep a lightweight `CommercialOperation[]` list and `simpleNewProjectDraftActive` so the first layer can expose project selection instead of silently using the first available project. A new project draft is not auto-replaced by the first existing project during refresh; the new operation is created only when the worker submits the goal.
- `simple-project-delete` calls `commercialOperationClient.delete`, which archives the selected project and removes it from the default project picker. This is a safe archive-delete, not a physical cascade delete.
- `simple-project-entry` displays the selected/current project, recent project options, and a new-project draft action.
- `simple-conversation-workspace` becomes the primary work area after project selection. It shows recent conversation messages, RAG context access, the overall operation plan state, and the goal input in one large chat surface.
- `simple-plan-review-card` routes generation through `advanceMainAgentProjectStep`, so the Main Agent creates a reviewable overall operation plan before downstream production steps.
- `submitSimpleOperationGoal` is the primary goal-submit path inside the large chat workspace. It records the user message, creates or uses the selected commercial operation, then calls `advanceMainAgentLoop` with `plan_first_goal_submit=true` instead of running the generic conversation playbook. The backend treats this flag as explicit plan-first intent and forces `operation_strategy`, so stale intervention or delivery routing cannot prevent the first approval-ready operation plan from being created or reused.
- `regenerateOperationPlanFromSimpleWorkspace` rejects the current draft or reviewable plan when present, then asks the Main Agent to regenerate a new reviewable plan from the operating goal and RAG context.
- `simple-rag-context-card` keeps RAG upload/update visible before plan generation through the existing knowledge page.
- The previous Phase 73U visual approval workbench remains below this first layer for plan, workflow, image/video, and RAG review after the plan-first step.

## Boundary

Phase 73V is frontend information architecture plus existing operator-click routing. It does not replace the RAG ingestion backend, does not guarantee every LLM response cites RAG evidence, does not approve plans automatically, does not approve records without an operator click, does not select output candidates without an operator click, does not physically delete project children, does not submit ComfyUI prompts, does not mutate workflow JSON, does not overwrite original workflow files, does not run OpenClaw actions, does not run Playwright, does not publish, does not click final submit, does not collect credentials, does not ingest analytics, does not restart services automatically, and does not bypass approval.
