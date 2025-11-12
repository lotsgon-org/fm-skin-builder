use rfd::FileDialog;
use tauri::{AppHandle, Manager};

#[tauri::command]
pub fn select_folder(dialog_title: Option<String>, initial_path: Option<String>) -> Option<String> {
    let mut dialog = FileDialog::new();

    if let Some(title) = dialog_title {
        dialog = dialog.set_title(&title);
    }

    if let Some(path) = initial_path {
        if !path.trim().is_empty() {
            dialog = dialog.set_directory(path);
        }
    }

    dialog
        .pick_folder()
        .map(|folder| folder.to_string_lossy().to_string())
}

#[tauri::command]
pub fn get_default_skins_dir(app_handle: AppHandle) -> Result<String, String> {
    let document_dir = app_handle
        .path()
        .document_dir()
        .map_err(|e| format!("Failed to get documents directory: {}", e))?;

    let skins_dir = document_dir.join("FM Skin Builder");
    Ok(skins_dir.to_string_lossy().to_string())
}

#[tauri::command]
pub fn ensure_skins_dir(app_handle: AppHandle) -> Result<String, String> {
    let document_dir = app_handle
        .path()
        .document_dir()
        .map_err(|e| format!("Failed to get documents directory: {}", e))?;

    let skins_dir = document_dir.join("FM Skin Builder");

    if !skins_dir.exists() {
        std::fs::create_dir_all(&skins_dir)
            .map_err(|e| format!("Failed to create skins directory: {}", e))?;
    }

    Ok(skins_dir.to_string_lossy().to_string())
}

#[tauri::command]
pub fn get_cache_dir(app_handle: AppHandle) -> Result<String, String> {
    let cache_dir = app_handle
        .path()
        .app_cache_dir()
        .map_err(|e| format!("Failed to get cache directory: {}", e))?;

    Ok(cache_dir.to_string_lossy().to_string())
}
