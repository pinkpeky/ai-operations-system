use tauri::{
    menu::{MenuBuilder, MenuItemBuilder},
    tray::{MouseButton, MouseButtonState, TrayIconBuilder, TrayIconEvent},
    App, AppHandle, Emitter, Manager, WindowEvent,
};

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
            update_tray_tooltip
        ])
        .run(tauri::generate_context!())
        .expect("error while running AI Ops Worker Desktop Console");
}
