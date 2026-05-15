import { invoke } from "@tauri-apps/api/core";
import { listen, UnlistenFn } from "@tauri-apps/api/event";

export type TrayControlAction =
  | "showConsole"
  | "hideWindow"
  | "startRuntime"
  | "stopRuntime"
  | "restartRuntime"
  | "startHeartbeat"
  | "stopHeartbeat"
  | "refreshStatus";

function isTauriRuntime(): boolean {
  return "__TAURI_INTERNALS__" in window;
}

export async function updateTrayTooltip(tooltip: string): Promise<void> {
  if (!isTauriRuntime()) {
    return;
  }

  try {
    await invoke("update_tray_tooltip", { tooltip });
  } catch {
    // 桌面桥接失败不影响 Web GUI 运行。
  }
}

export async function showConsoleWindow(): Promise<void> {
  if (!isTauriRuntime()) {
    return;
  }
  await invoke("show_console_window");
}

export async function hideConsoleWindow(): Promise<void> {
  if (!isTauriRuntime()) {
    return;
  }
  await invoke("hide_console_window");
}

export async function startWorkerClientRuntime(): Promise<string> {
  if (!isTauriRuntime()) {
    throw new Error("Native runtime launch is only available inside the Tauri desktop app.");
  }
  return await invoke<string>("start_worker_client_runtime");
}

export async function listenForTrayControls(handler: (action: TrayControlAction) => void): Promise<UnlistenFn | null> {
  if (!isTauriRuntime()) {
    return null;
  }

  return listen<TrayControlAction>("tray-control", (event) => {
    handler(event.payload);
  });
}
