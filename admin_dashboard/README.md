# AI Ops Admin Dashboard

Phase 36 introduces a read-only Server Admin Dashboard foundation for the AI Operations System.

## Scope

The dashboard is a standalone Vite + React + TypeScript + Tailwind project. It monitors the AI Server and currently includes:

- Overview
- Workers
- Browser Runtime
- Conversations
- Tasks
- OpenClaw mock status
- Audit Logs
- RAG / Documents
- Settings

This is a monitoring foundation only. It does not include a login UI, permission UI, publishing business flow, production-grade operations workflows, or real social platform control.

## Configuration

Copy `.env.example` to `.env` when needed:

```env
VITE_AI_SERVER_API=http://localhost:8000
VITE_WORKSPACE_ID=demo-workspace
VITE_USER_ID=demo-user
```

The Settings page can also save the AI Server URL, workspace ID, and user ID to localStorage.

## Development

```powershell
cd admin_dashboard
npm install
npm run dev
```

Open:

```text
http://localhost:5180
```

## Build

```powershell
cd admin_dashboard
npm run build
```

The dashboard is not currently wired into `docker-compose.yml`; Phase 36 only requires static build verification.
