#![cfg_attr(not(debug_assertions), windows_subsystem = "windows")]

mod commands;
mod events;
mod paths;
mod process;

use commands::{ensure_skins_dir, get_cache_dir, get_default_skins_dir, select_folder};
use paths::{detect_game_installation, find_bundles_in_game_dir};
use process::{run_python_task, stop_python_task, ProcessState};
use tauri::Manager;

fn main() {
    tauri::Builder::default()
        .manage(ProcessState::default())
        .invoke_handler(tauri::generate_handler![
            run_python_task,
            stop_python_task,
            select_folder,
            get_default_skins_dir,
            ensure_skins_dir,
            get_cache_dir,
            detect_game_installation,
            find_bundles_in_game_dir
        ])
        .setup(|app| {
            // Create skins directory on app startup
            let app_handle = app.handle().clone();
            if let Ok(document_dir) = app_handle.path().document_dir() {
                let skins_dir = document_dir.join("FM Skin Builder");
                if !skins_dir.exists() {
                    let _ = std::fs::create_dir_all(&skins_dir);
                }
            }
            Ok(())
        })
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}
