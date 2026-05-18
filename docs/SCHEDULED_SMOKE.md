# Scheduled Smoke

Updated: 2026-05-18

This document records the scheduled server smoke posture for the Phase 56 readiness track.

## Workflow

File:

```text
.github/workflows/server-docker-smoke.yml
```

The workflow can run in two modes:

- Scheduled: daily at `19:00 UTC`, which is `03:00 Asia/Shanghai` on the next calendar day.
- Manual: `workflow_dispatch` with one of `server-docker`, `staging`, or `production-like`.

Scheduled runs use:

```text
server-docker
```

Manual runs use the selected profile.

## Artifacts

Successful runs upload:

```text
<profile>-readiness-report
```

Failed runs also upload:

```text
server-docker-smoke-logs
```

The readiness report is generated under `release/reports/ci/` during CI and is ignored locally.

## Concurrency

The workflow uses a non-cancelling concurrency group per ref:

```text
server-docker-smoke-${{ github.ref }}
```

This avoids overlapping scheduled/manual runs for the same ref while preserving an already-running smoke.

## Acceptance

A scheduled smoke is accepted when:

- Docker compose config validates.
- Docker compose stack builds and starts.
- API health returns HTTP 2xx.
- Deployment profile verification passes.
- Release smoke matrix passes with `--strict`.
- Readiness report artifact uploads.
- Compose stack shuts down in the final cleanup step.

## Boundaries

- This is not a production uptime monitor.
- This does not page or notify anyone by itself.
- This does not add deployment secrets.
- This does not replace release-sensitive manual smoke before major changes.
