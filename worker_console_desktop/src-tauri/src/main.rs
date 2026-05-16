use tauri::{
    menu::{MenuBuilder, MenuItemBuilder},
    tray::{MouseButton, MouseButtonState, TrayIconBuilder, TrayIconEvent},
    App, AppHandle, Emitter, Manager, WindowEvent,
};
use std::path::{Path, PathBuf};
use std::net::TcpListener;
use std::process::{Command, Stdio};

#[cfg(target_os = "windows")]
use std::os::windows::process::CommandExt;

const MAIN_WINDOW_LABEL: &str = "main";
const TRAY_ID: &str = "main-tray";
const MINIMIZE_TO_TRAY: bool = true;

fn show_main_window(app: &AppHandle) -> Result<(), String> {
    let window = app
        .get_webview_window(MAIN_WINDOW_LABEL)
        .ok_or_else(|| "main window not found".to_string())?;
    window.show().map_err(|error| error.to_string())?;
    window.set_focus().map_err(|error| error.to_string())?;
    Ok(())
}

fn hide_main_window(app: &AppHandle) -> Result<(), String> {
    let window = app
        .get_webview_window(MAIN_WINDOW_LABEL)
        .ok_or_else(|| "main window not found".to_string())?;
    window.hide().map_err(|error| error.to_string())?;
    Ok(())
}

fn emit_tray_control(app: &AppHandle, action: &str) {
    let _ = app.emit("tray-control", action.to_string());
    let _ = show_main_window(app);
}

fn is_workspace_root(path: &Path) -> bool {
    path.join("worker_client").join("cli.py").exists()
        && path.join("worker_console_desktop").join("src-tauri").exists()
}

fn find_workspace_root() -> Result<PathBuf, String> {
    let mut candidates = Vec::new();
    if let Ok(current_dir) = std::env::current_dir() {
        candidates.push(current_dir);
    }
    if let Ok(current_exe) = std::env::current_exe() {
        if let Some(parent) = current_exe.parent() {
            candidates.push(parent.to_path_buf());
        }
    }

    for candidate in candidates {
        for ancestor in candidate.ancestors() {
            if is_workspace_root(ancestor) {
                return Ok(ancestor.to_path_buf());
            }
        }
    }

    Err("AI Ops workspace root not found. Start worker_client with the packaging script or run Tauri from the repository checkout.".to_string())
}

fn read_runtime_port(config_path: &Path) -> u16 {
    let Ok(config_text) = std::fs::read_to_string(config_path) else {
        return 9100;
    };

    for line in config_text.lines() {
        let trimmed = line.trim();
        if let Some(value) = trimmed.strip_prefix("runtime_port:") {
            if let Ok(port) = value.trim().parse::<u16>() {
                return port;
            }
        }
    }

    9100
}

fn ensure_runtime_port_available(port: u16) -> Result<(), String> {
    match TcpListener::bind(("127.0.0.1", port)) {
        Ok(listener) => {
            drop(listener);
            Ok(())
        }
        Err(error) => Err(format!(
            "port_conflict: port {} already in use. Suggest changing runtime_port or stopping conflicting service. server_environment_warning: Desktop Console controls the worker runtime on this local machine; if running on the server host, Start Runtime starts a server-local worker, not a remote customer machine. Detail: {}",
            port, error
        )),
    }
}

#[tauri::command]
fn show_console_window(app: AppHandle) -> Result<(), String> {
    show_main_window(&app)
}

#[tauri::command]
fn hide_console_window(app: AppHandle) -> Result<(), String> {
    hide_main_window(&app)
}

#[tauri::command]
fn update_tray_tooltip(app: AppHandle, tooltip: String) -> Result<(), String> {
    let tray = app
        .tray_by_id(TRAY_ID)
        .ok_or_else(|| "tray icon not found".to_string())?;
    tray.set_tooltip(Some(tooltip.as_str()))
        .map_err(|error| error.to_string())
}

#[tauri::command]
fn start_worker_client_runtime() -> Result<String, String> {
    let workspace_root = find_workspace_root()?;
    let config_path = workspace_root.join("worker_client").join("worker_config.yaml");
    if !config_path.exists() {
        return Err(format!(
            "missing_config: missing worker config. Copy worker_config.example.yaml first. Expected path: {}.",
            config_path.display()
        ));
    }

    let runtime_port = read_runtime_port(&config_path);
    ensure_runtime_port_available(runtime_port)?;

    let launch_attempts: [(&str, &[&str]); 3] = [
        ("python", &["-m"]),
        ("py", &["-3", "-m"]),
        ("python3", &["-m"]),
    ];
    let mut errors = Vec::new();

    for (executable, prefix_args) in launch_attempts {
        let mut command = Command::new(executable);
        command
            .args(prefix_args)
            .arg("worker_client.cli")
            .arg("--config")
            .arg(&config_path)
            .arg("start")
            .current_dir(&workspace_root)
            .env("PYTHONUTF8", "1")
            .stdin(Stdio::null())
            .stdout(Stdio::null())
            .stderr(Stdio::null());

        #[cfg(target_os = "windows")]
        {
            const CREATE_NO_WINDOW: u32 = 0x08000000;
            command.creation_flags(CREATE_NO_WINDOW);
        }

        match command.spawn() {
            Ok(child) => {
                return Ok(format!(
                    "worker_client start launched with {} (pid {}). Waiting for http://127.0.0.1:9100/local/status.",
                    executable,
                    child.id()
                ));
            }
            Err(error) => errors.push(format!("{}: {}", executable, error)),
        }
    }

    Err(format!(
        "failed: Unable to launch worker_client. Install Python or start manually with: python -m worker_client.cli --config {} start. Attempts: {}",
        config_path.display(),
        errors.join("; ")
    ))
}

fn attach_minimize_to_tray_handler(app: &App) {
    if !MINIMIZE_TO_TRAY {
        return;
    }

    if let Some(window) = app.get_webview_window(MAIN_WINDOW_LABEL) {
        let window_for_handler = window.clone();
        window.on_window_event(move |event| {
            if let WindowEvent::CloseRequested { api, .. } = event {
                api.prevent_close();
                let _ = window_for_handler.hide();
            }
        });
    }
}

fn build_system_tray(app: &App) -> tauri::Result<()> {
    let show_console = MenuItemBuilder::with_id("show_console", "Show Console").build(app)?;
    let hide_window = MenuItemBuilder::with_id("hide_window", "Hide Window").build(app)?;
    let start_runtime = MenuItemBuilder::with_id("start_runtime", "Start Runtime").build(app)?;
    let stop_runtime = MenuItemBuilder::with_id("stop_runtime", "Stop Runtime").build(app)?;
    let restart_runtime = MenuItemBuilder::with_id("restart_runtime", "Restart Runtime").build(app)?;
    let start_heartbeat = MenuItemBuilder::with_id("start_heartbeat", "Start Heartbeat").build(app)?;
    let stop_heartbeat = MenuItemBuilder::with_id("stop_heartbeat", "Stop Heartbeat").build(app)?;
    let refresh_status = MenuItemBuilder::with_id("refresh_status", "Refresh Status").build(app)?;
    let quit = MenuItemBuilder::with_id("quit", "Quit").build(app)?;

    let menu = MenuBuilder::new(app)
        .items(&[
            &show_console,
            &hide_window,
            &start_runtime,
            &stop_runtime,
            &restart_runtime,
            &start_heartbeat,
            &stop_heartbeat,
            &refresh_status,
            &quit,
        ])
        .build()?;

    TrayIconBuilder::with_id(TRAY_ID)
        .tooltip("AI Ops Worker Console\nstatus: disconnected")
        .menu(&menu)
        .show_menu_on_left_click(false)
        .on_menu_event(|app, event| match event.id.as_ref() {
            "show_console" => {
                let _ = show_main_window(app);
            }
            "hide_window" => {
                let _ = hide_main_window(app);
            }
            "start_runtime" => emit_tray_control(app, "startRuntime"),
            "stop_runtime" => emit_tray_control(app, "stopRuntime"),
            "restart_runtime" => emit_tray_control(app, "restartRuntime"),
            "start_heartbeat" => emit_tray_control(app, "startHeartbeat"),
            "stop_heartbeat" => emit_tray_control(app, "stopHeartbeat"),
            "refresh_status" => emit_tray_control(app, "refreshStatus"),
            "quit" => app.exit(0),
            _ => {}
        })
        .on_tray_icon_event(|tray, event| {
            if let TrayIconEvent::Click {
                button: MouseButton::Left,
                button_state: MouseButtonState::Up,
                ..
            } = event
            {
                let _ = show_main_window(&tray.app_handle());
            }
        })
        .build(app)?;

    Ok(())
}

fn main() {
    tauri::Builder::default()
        .setup(|app| {
            build_system_tray(app)?;
            attach_minimize_to_tray_handler(app);
            Ok(())
        })
        .invoke_handler(tauri::generate_handler![
            show_console_window,
            hide_console_window,
            update_tray_tooltip,
            start_worker_client_runtime
        ])
        .run(tauri::generate_context!())
        .expect("error while running AI Ops Worker Desktop Console");
}
