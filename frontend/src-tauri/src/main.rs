#![cfg_attr(not(debug_assertions), windows_subsystem = "windows")]

use rfd::FileDialog;
use serde::{Deserialize, Serialize};
use std::{path::PathBuf, process::Stdio};
use tauri::{path::BaseDirectory, AppHandle, Emitter, Manager};
use tokio::io::{AsyncBufReadExt, BufReader};
use tokio::process::Command;

#[derive(Serialize, Clone)]
struct LogEvent {
    message: String,
    level: String, // "info", "error", "warning"
}

#[derive(Serialize, Clone)]
struct ProgressEvent {
    current: u32,
    total: u32,
    status: String,
}

#[derive(Serialize, Clone)]
struct CompletionEvent {
    success: bool,
    exit_code: i32,
    message: String,
}

#[derive(Serialize)]
struct CommandResult {
    stdout: String,
    stderr: String,
    status: i32,
}

#[derive(Deserialize)]
#[serde(rename_all = "camelCase")]
struct TaskConfig {
    skin_path: String,
    bundles_path: String,
    debug_export: bool,
    dry_run: bool,
}

fn workspace_root() -> PathBuf {
    PathBuf::from(env!("CARGO_MANIFEST_DIR"))
        .parent()
        .and_then(|path| path.parent())
        .map(|path| path.to_path_buf())
        .unwrap_or_else(|| PathBuf::from("."))
}

fn python_command() -> PathBuf {
    let root = workspace_root();
    let mut unix_path = root.clone();
    unix_path.push(".venv/bin/python3");

    if unix_path.exists() {
        return unix_path;
    }

    let mut win_path = root.clone();
    win_path.push(".venv/Scripts/python.exe");
    if win_path.exists() {
        return win_path;
    }

    if cfg!(windows) {
        PathBuf::from("python.exe")
    } else {
        PathBuf::from("python3")
    }
}

fn build_cli_args(config: &TaskConfig) -> Result<Vec<String>, String> {
    let skin = config.skin_path.trim();
    if skin.is_empty() {
        return Err("Skin folder is required.".to_string());
    }

    let mut args = vec!["patch".to_string(), skin.to_string()];

    let bundles = config.bundles_path.trim();
    if !bundles.is_empty() {
        args.push("--bundle".to_string());
        args.push(bundles.to_string());
    }

    if config.debug_export {
        args.push("--debug-export".to_string());
    }

    if config.dry_run {
        args.push("--dry-run".to_string());
    }

    Ok(args)
}

/// Parse progress information from log lines
/// Expected format: "=== Patching bundle X of Y: path/to/bundle ==="
/// Or: "🔍 Scanning bundle: name (X/Y)"
fn parse_progress(line: &str) -> Option<(u32, u32, String)> {
    // Pattern 1: "=== Patching bundle: path ===" followed by total count
    if line.contains("=== Patching bundle:") {
        // Try to extract bundle name
        if let Some(start) = line.find("bundle:") {
            let bundle_part = &line[start + 7..].trim();
            if let Some(end) = bundle_part.find("===") {
                let bundle_name = bundle_part[..end].trim();
                return Some((0, 0, format!("Processing: {}", bundle_name)));
            }
        }
    }

    // Pattern 2: Look for progress indicators in format "X of Y" or "X/Y"
    if line.contains(" of ") || line.contains("/") {
        // Simple heuristic: if we see numbers in format "X of Y"
        let words: Vec<&str> = line.split_whitespace().collect();
        for i in 0..words.len().saturating_sub(2) {
            if words[i + 1] == "of" {
                if let (Ok(current), Ok(total)) = (words[i].parse::<u32>(), words[i + 2].parse::<u32>()) {
                    let status = line.split("===").next().unwrap_or(line).trim().to_string();
                    return Some((current, total, status));
                }
            }
        }
    }

    None
}

/// Determine log level from line content
fn get_log_level(line: &str) -> String {
    let line_upper = line.to_uppercase();
    if line_upper.contains("ERROR") || line_upper.contains("✗") || line_upper.contains("[STDERR]") {
        "error".to_string()
    } else if line_upper.contains("WARN") || line_upper.contains("WARNING") {
        "warning".to_string()
    } else {
        "info".to_string()
    }
}

#[tauri::command]
async fn run_python_task(app_handle: AppHandle, config: TaskConfig) -> Result<CommandResult, String> {
    let cli_args = build_cli_args(&config)?;

    // Build the command
    let mut command = if cfg!(debug_assertions) {
        let mut cmd = Command::new(python_command());
        cmd.arg("-m").arg("fm_skin_builder");
        cmd.current_dir(workspace_root());
        cmd.env("PYTHONPATH", "fm_skin_builder");
        cmd
    } else {
        let binary_name = if cfg!(windows) {
            "resources/backend/fm_skin_builder.exe"
        } else {
            "resources/backend/fm_skin_builder"
        };

        let backend_binary = app_handle
            .path()
            .resolve(binary_name, BaseDirectory::Resource)
            .map_err(|error| format!("Failed to resolve backend binary path: {error}"))?;

        if !backend_binary.exists() {
            return Err(format!(
                "Backend binary not found at: {}\nExpected binary name: {}",
                backend_binary.display(),
                binary_name
            ));
        }

        Command::new(backend_binary)
    };

    command.args(&cli_args);
    command.stdout(Stdio::piped());
    command.stderr(Stdio::piped());

    // Hide console window on Windows
    #[cfg(windows)]
    {
        use std::os::windows::process::CommandExt;
        const CREATE_NO_WINDOW: u32 = 0x08000000;
        command.creation_flags(CREATE_NO_WINDOW);
    }

    // Spawn the process
    let mut child = command
        .spawn()
        .map_err(|error| format!("Failed to spawn process: {error}"))?;

    // Get stdout and stderr handles
    let stdout = child.stdout.take().ok_or("Failed to capture stdout")?;
    let stderr = child.stderr.take().ok_or("Failed to capture stderr")?;

    // Create buffered readers
    let mut stdout_reader = BufReader::new(stdout).lines();
    let mut stderr_reader = BufReader::new(stderr).lines();

    // Storage for complete output (for backward compatibility)
    let mut stdout_lines = Vec::new();
    let mut stderr_lines = Vec::new();

    // Progress tracking
    let mut current_progress = 0u32;
    let mut total_progress = 0u32;

    // Stream stdout
    let app_handle_stdout = app_handle.clone();
    let stdout_task = tokio::spawn(async move {
        let mut lines = Vec::new();
        while let Ok(Some(line)) = stdout_reader.next_line().await {
            lines.push(line.clone());

            // Parse for progress information
            if let Some((current, total, status)) = parse_progress(&line) {
                if total > 0 {
                    let _ = app_handle_stdout.emit(
                        "build_progress",
                        ProgressEvent {
                            current,
                            total,
                            status,
                        },
                    );
                }
            }

            // Emit log event
            let level = get_log_level(&line);
            let _ = app_handle_stdout.emit(
                "build_log",
                LogEvent {
                    message: line,
                    level,
                },
            );
        }
        lines
    });

    // Stream stderr
    let app_handle_stderr = app_handle.clone();
    let stderr_task = tokio::spawn(async move {
        let mut lines = Vec::new();
        while let Ok(Some(line)) = stderr_reader.next_line().await {
            lines.push(line.clone());

            // Emit stderr as error log
            let _ = app_handle_stderr.emit(
                "build_log",
                LogEvent {
                    message: format!("[STDERR] {}", line),
                    level: "error".to_string(),
                },
            );
        }
        lines
    });

    // Wait for process to complete
    let exit_status = child
        .wait()
        .await
        .map_err(|error| format!("Failed to wait for process: {error}"))?;

    // Wait for all output to be consumed
    stdout_lines = stdout_task
        .await
        .map_err(|error| format!("Failed to read stdout: {error}"))?;
    stderr_lines = stderr_task
        .await
        .map_err(|error| format!("Failed to read stderr: {error}"))?;

    let exit_code = exit_status.code().unwrap_or(-1);
    let success = exit_status.success();

    // Emit completion event
    let _ = app_handle.emit(
        "build_complete",
        CompletionEvent {
            success,
            exit_code,
            message: if success {
                "Build completed successfully".to_string()
            } else {
                format!("Build failed with exit code {}", exit_code)
            },
        },
    );

    Ok(CommandResult {
        stdout: stdout_lines.join("\n"),
        stderr: stderr_lines.join("\n"),
        status: exit_code,
    })
}

#[tauri::command]
fn select_folder(dialog_title: Option<String>, initial_path: Option<String>) -> Option<String> {
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

#[cfg_attr(mobile, tauri::mobile_entry_point)]
fn main() {
    tauri::Builder::default()
        .invoke_handler(tauri::generate_handler![run_python_task, select_folder])
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}
