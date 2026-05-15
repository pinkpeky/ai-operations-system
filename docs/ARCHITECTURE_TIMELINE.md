# Architecture Timeline

This document records how the system evolved across Phase 1-52. It is the architecture recovery log for new Codex conversations and release-readiness reviews.

## Runtime Evolution

- Phase 1-6: API, database, cache, vector store, local LLM, and embedding foundations.
- Phase 7-14: Agentic RAG, lifecycle, hybrid search, reranking, eval/trace, file upload, and docs runtime verification.
- Phase 15-23: Task, tool, memory, multi-agent, planning, browser adapter, and browser profile reliability foundations.
- Phase 24-32: Human browser control, UI access placeholder, worker security, customer worker bootstrap, OpenClaw mock adapter, worker console, desktop shell, and tray/runtime foundation.
- Phase 33-42: Conversation runtime, remote browser runtime, browser observability, admin dashboard, tool bridge, approvals, playbooks, artifacts, and background task orchestration.
- Phase 43-52: Scheduler recovery, artifact pipeline, workflow state, workflow graph runtime, template registry, governance, workflow observability, desktop packaging readiness, release bundle foundation, and deployment profiles.

## Workflow Evolution

Plans evolve into playbooks, playbooks evolve into workflow state, workflow state evolves into graph runtime, graph runtime evolves into template registry, and templates gain governance and observability. The workflow system remains a foundation, not a full visual DAG editor or distributed orchestration engine.

## Artifact Evolution

Outputs begin as assistant messages and playbook results, become output artifacts, gain lineage and export packaging, then connect to workflow runs, steps, checkpoints, templates, traces, replay sessions, and diagnostics.

## Replay Evolution

Browser replay begins as metadata-only browser runtime replay. Workflow replay adds checkpoint metadata and replay sessions. The current system supports metadata-only and dry-run replay foundations, not deterministic re-execution.

## Governance Evolution

The governance path starts with conversation approval and risk policy, extends to playbook approval integration, then adds template review queues, lifecycle transitions, rollback, audit logs, compatibility matrices, and internal marketplace badges.

## Packaging Evolution

Packaging begins with worker/client scripts, then desktop shell readiness, release manifest/version metadata, bundle validation scripts, and deployment profile bootstrapping. Current packaging is readiness infrastructure only, not final signed installers or auto-update.

## Deployment Evolution

Deployment starts with Docker Compose and local development defaults. Phase 52 introduces local-dev, server-docker, client-worker, desktop-client, staging, and production-like profiles with env generation, dependency checks, port checks, startup scripts, and health verification. Phase 53 adds a release smoke matrix, unified preflight runner, release readiness report, migration continuity check, and runtime hygiene check. It is not Kubernetes, Helm, Terraform, Ansible, CI/CD SaaS, or production HA automation.
