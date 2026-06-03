# Phase 73I Server Operation Context Drawer

Phase 73I continues the server backend simplification after Phase 73H. The Commercial Ops page should keep the operation list visible while folding selected-operation context into a single quiet drawer, instead of showing full operation details and Agent/Skill orchestration as two always-open panels.

## Implementation

- `admin_dashboard/src/main.tsx` adds `commercial-server-operation-context-drawer` with aria label `Phase 73I Server Operation Context Drawer`.
- The drawer summary shows the selected operation title, status, production closed-loop primary step, and Agent/Skill orchestration status when an operation is selected.
- The existing operation detail `Panel`, plan table, status action buttons, Agent/Skill summary, skill table, and routing decision table remain available inside `commercial-server-operation-context-body`.
- Phase 73G and Phase 73H remain intact: the quiet server cockpit, maintenance drawer, and create-operation drawer still appear before the operation list and operation context drawer.

## Boundaries

This is frontend information architecture only. It does not remove operation details, remove Agent/Skill orchestration, remove plan regeneration, remove status actions, change commercial operation APIs, create operations automatically, approve records, reject records, acknowledge intervention records without an operator click, call target endpoints, run OpenClaw, run Playwright, publish, submit ComfyUI prompts, mutate workflow JSON, ingest analytics, configure secrets, restart services, or bypass approval.

## Verification

- `admin_dashboard` typecheck should pass.
- Commercial operations docs/tests should assert that Phase 73I is documented and that operation details plus Agent/Skill orchestration are folded behind `commercial-server-operation-context-drawer` by default.
- Browser verification on `http://127.0.0.1:5173/` should confirm that the operation context drawer is closed by default, expands to reveal operation details and Agent/Skill controls, and does not create horizontal page overflow.
