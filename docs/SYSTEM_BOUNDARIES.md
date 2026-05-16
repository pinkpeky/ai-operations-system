# Explicit Non-Goals

The AI Operations System is not currently a real social media automation platform, public marketplace, production CI/CD platform, distributed orchestration engine, or stealth browser bypass framework.

# Mocked Components

- LLM provider can run in mock mode.
- Embedding provider can run in mock mode.
- Reranker provider can run in mock mode.
- OpenClaw provider is mock-only.
- Some browser/tool flows use mock or placeholder providers when no worker is available.

# Simulated Integrations

- OpenClaw actions are mock actions.
- Template marketplace is an internal governance foundation, not a public marketplace.
- Replay systems generate metadata, summaries, diagnostics, and dry-run records; they are not deterministic re-execution engines.

# Browser Runtime Boundaries

- No TikTok, YouTube, or X automation.
- No automatic login.
- No cookie injection.
- No captcha bypass.
- No proxy pool.
- No fingerprint or anti-detect bypass.
- No stealth browser framework.
- No VNC/noVNC/DevTools remote-control implementation in the current foundation.

# Worker Runtime Boundaries

- Worker clients must protect `worker_secret` locally.
- `worker_state.json`, logs, runtime state, and generated screenshots must not be committed.
- Customer-machine E2E validation must run on the customer machine; server-local validation does not prove remote customer-machine control.

# Desktop Runtime Boundaries

- Worker Console Desktop controls the local machine runtime only.
- It is not a signed installer.
- It has no auto updater.
- It has no production MSI/EXE/DMG/notarized package.
- It is not a system-management or remote-shell tool.

# Security Boundaries

- Phase 39 approval gates are safety foundations, not a complete permission system.
- Worker signing and audit logs are foundations, not a full enterprise IAM layer.
- No secrets, tokens, `.env`, worker state, logs, runtime state, or generated storage artifacts should be committed.

# Deployment Boundaries

- Deployment profiles are bootstrap guides and validation helpers.
- The project currently is not Kubernetes, Helm, Terraform, Ansible, or production HA deployment automation.
- Docker Compose validation is the current server deployment foundation.

# Packaging Boundaries

- Release packaging is readiness metadata and scripts only.
- No code signing.
- No auto-update channel.
- No formal installer publishing.
- No production object-storage platform, CDN, or video-transcoding pipeline.

# Explicitly Not Implemented

- distributed orchestration engine
- real OpenClaw
- real social media automation
- stealth browser bypass framework
- production CI/CD platform
