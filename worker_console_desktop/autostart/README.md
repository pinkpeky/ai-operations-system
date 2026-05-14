# AutoStart Placeholder

Phase 32 adds only an AutoStart placeholder for the Worker Console Desktop Runtime Foundation.

Planned future directions:

- Windows registry startup
- macOS LaunchAgent
- start on login

Current boundary:

- no autostart registration
- no installer integration
- no auto update
- no background service installer
- start on login is not implemented

Operators must still start the Worker Console Desktop manually with:

```powershell
cd worker_console_desktop
npm run tauri dev
```
