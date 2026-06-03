# Phase 73X Main Agent LLM Operation Plan

## Scope

Phase 73X connects the plan-first customer-machine workspace to the real Main Agent LLM planning path. When the operator submits an operating goal, `CommercialOperationService._advance_operation_strategy` now builds the first `OperationPlan` from `LLMClient` structured JSON when the configured provider is reachable and returns parseable JSON.

The planning contract records its source in `plan_metadata.main_agent_advance`:

- `plan_generation_contract=main_agent_llm_structured_json_with_template_fallback`
- `plan_generation_source=llm` when the LLM payload is parsed and stored
- `plan_generation_source=fallback` when health, generation, or JSON parsing fails
- `llm_generation_status` for `parsed`, `unreachable`, `unparseable_json`, or `failed`
- `regeneration_attempt` and `previous_rejected_plan_count` so "regenerate" can produce a materially different strategy
- `rag_context_status=collection_name_only_no_retrieved_chunks` when a knowledge collection is configured but retrieved chunks are not injected into this prompt

## Behavior

The LLM must return JSON fields for `title`, `objective_summary`, `audience_strategy`, `channel_strategy`, `content_strategy`, `production_scope`, `material_requirements`, `kpis`, `publish_schedule`, and `risk_notes`. The service sanitizes those fields before creating the `OperationPlan`, preserves copy/image/media production task coverage when the fallback scope requires it, and keeps workflow execution behind human approval.

Regeneration passes the latest rejected-plan context and a specific regeneration focus into the prompt. If the provider is unavailable or returns non-JSON, the deterministic operation-plan template remains a safe fallback, but metadata exposes that it was not LLM-authored.

## Boundaries

Phase 73X does not submit ComfyUI prompts, mutate workflow JSON, publish, run OpenClaw, run Playwright, collect platform analytics, approve records without an operator click, inject retrieved RAG chunks into the operation-plan prompt, guarantee RAG citation quality, or bypass approval.

## Verification

- `.\.venv\Scripts\python.exe -m pytest tests\test_commercial_operation_main_agent_advance.py -q`
