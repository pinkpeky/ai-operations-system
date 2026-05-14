export type DesktopSettings = {
  localWorkerApi: string;
  minimizeToTray: boolean;
  refreshIntervalMs: number;
};

export const defaultDesktopSettings: DesktopSettings = {
  localWorkerApi: import.meta.env.VITE_LOCAL_WORKER_API ?? "http://127.0.0.1:9100",
  minimizeToTray: true,
  refreshIntervalMs: 5000,
};

function normalizeSettings(input: Partial<DesktopSettings>): DesktopSettings {
  const refreshIntervalMs = Number(input.refreshIntervalMs ?? defaultDesktopSettings.refreshIntervalMs);

  return {
    localWorkerApi: (input.localWorkerApi ?? defaultDesktopSettings.localWorkerApi).replace(/\/$/, ""),
    minimizeToTray: input.minimizeToTray ?? defaultDesktopSettings.minimizeToTray,
    refreshIntervalMs: Number.isFinite(refreshIntervalMs) && refreshIntervalMs >= 1000 ? refreshIntervalMs : 5000,
  };
}

export async function loadDesktopSettings(): Promise<DesktopSettings> {
  try {
    const response = await fetch("/settings.json", { cache: "no-store" });
    if (!response.ok) {
      return normalizeSettings({});
    }

    const fileSettings = (await response.json()) as Partial<DesktopSettings>;
    return normalizeSettings(fileSettings);
  } catch {
    return normalizeSettings({});
  }
}
