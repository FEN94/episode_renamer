import os
import re
import customtkinter as ctk
from tkinter import filedialog

ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")

class EpisodeRenamer(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Episode Renamer")
        self.geometry("1000x680")

        self.folder_path = ""
        self.file_entries = []  # Stores (original_filename, CTkEntry, CTkLabel_Preview) tuples
        self.last_rename_history = []  # Stores list of (old_full_path, new_full_path) for rollback

        # --- Top Control Panel ---
        self.top_frame = ctk.CTkFrame(self)
        self.top_frame.pack(pady=10, padx=10, fill="x")

        self.btn_select_folder = ctk.CTkButton(self.top_frame, text="Select Folder", command=self.select_folder)
        self.btn_select_folder.grid(row=0, column=0, padx=5, pady=5)

        self.entry_folder = ctk.CTkEntry(self.top_frame, placeholder_text="No folder selected")
        self.entry_folder.grid(row=0, column=1, columnspan=4, padx=5, pady=5, sticky="ew")

        # Show Name Input
        ctk.CTkLabel(self.top_frame, text="Show Name:").grid(row=1, column=0, padx=5, pady=5, sticky="e")
        self.entry_show_name = ctk.CTkEntry(self.top_frame, placeholder_text="e.g., Breaking Bad")
        self.entry_show_name.grid(row=1, column=1, columnspan=2, padx=5, pady=5, sticky="ew")
        self.entry_show_name.bind("<KeyRelease>", lambda event: self.update_all_previews())

        # Season Input
        ctk.CTkLabel(self.top_frame, text="Season Number:").grid(row=1, column=3, padx=5, pady=5, sticky="e")
        self.entry_season = ctk.CTkEntry(self.top_frame, placeholder_text="e.g., 1")
        self.entry_season.grid(row=1, column=4, padx=5, pady=5, sticky="ew")
        self.entry_season.bind("<KeyRelease>", lambda event: self.update_all_previews())

        self.top_frame.columnconfigure(1, weight=1)
        self.top_frame.columnconfigure(2, weight=1)
        self.top_frame.columnconfigure(4, weight=1)

        # Action Buttons
        self.btn_load = ctk.CTkButton(self.top_frame, text="Load Files", command=self.load_files)
        self.btn_load.grid(row=2, column=0, padx=5, pady=10, sticky="ew")

        self.btn_detect_regex = ctk.CTkButton(self.top_frame, text="Detect EP via Regex", command=self.detect_episodes_regex)
        self.btn_detect_regex.grid(row=2, column=1, padx=5, pady=10, sticky="ew")

        self.btn_autofill = ctk.CTkButton(self.top_frame, text="Sequential Fill", command=self.auto_fill_sequential)
        self.btn_autofill.grid(row=2, column=2, padx=5, pady=10, sticky="ew")

        self.btn_undo = ctk.CTkButton(self.top_frame, text="Undo Rename", fg_color="orange", hover_color="darkorange", state="disabled", command=self.undo_rename)
        self.btn_undo.grid(row=2, column=3, padx=5, pady=10, sticky="ew")

        self.btn_rename = ctk.CTkButton(self.top_frame, text="Start Rename", fg_color="green", hover_color="darkgreen", command=self.rename_files)
        self.btn_rename.grid(row=2, column=4, padx=5, pady=10, sticky="ew")

        # --- Table / Scrollable Frame Panel ---
        self.table_frame = ctk.CTkScrollableFrame(self, label_text="Files")
        self.table_frame.pack(pady=(10, 5), padx=10, fill="both", expand=True)

        # --- Status Bar & Progress Indicator Panel ---
        self.status_frame = ctk.CTkFrame(self)
        self.status_frame.pack(pady=(0, 10), padx=10, fill="x")

        self.progress_bar = ctk.CTkProgressBar(self.status_frame)
        self.progress_bar.pack(fill="x", padx=10, pady=(8, 4))
        self.progress_bar.set(0)

        self.lbl_status = ctk.CTkLabel(self.status_frame, text="Ready", anchor="w", font=ctk.CTkFont(size=12))
        self.lbl_status.pack(fill="x", padx=10, pady=(0, 6))

    def set_status(self, text: str, text_color: str = None):
        """Helper to update status label text and color non-blockingly."""
        if text_color:
            self.lbl_status.configure(text=text, text_color=text_color)
        else:
            self.lbl_status.configure(text=text, text_color=("black", "white"))

    def select_folder(self):
        path = filedialog.askdirectory()
        if path:
            self.folder_path = path
            self.entry_folder.delete(0, "end")
            self.entry_folder.insert(0, self.folder_path)

    def extract_episode_number(self, filename: str) -> str:
        """Uses Regex patterns to find episode numbers in common release formats."""
        name_without_ext = os.path.splitext(filename)[0]

        patterns = [
            r'[Ss]\d+[Ee](\d+)',        # S01E02 / s01e02 -> 02
            r'\d+[Xx](\d+)',             # 1x02 / 1X02 -> 02
            r'[Ee][Pp]?\s*(\d+)',        # EP02 / ep.02 / E02 -> 02
            r'(?:[^\d]|^)(\d{1,3})(?:[^\d]|$)' # Standalone 1 to 3 digit numbers -> 02
        ]

        for pattern in patterns:
            match = re.search(pattern, name_without_ext)
            if match:
                ep_num = int(match.group(1))
                return f"{ep_num:02d}"

        return ""

    def generate_preview_name(self, original_filename: str, ep_str: str) -> str:
        """Helper to construct the expected new filename."""
        show_name = self.entry_show_name.get().strip()
        season_str = self.entry_season.get().strip()

        if not show_name or not season_str.isdigit() or not ep_str.isdigit():
            return "-"

        season_num = int(season_str)
        ep_num = int(ep_str)
        ext = os.path.splitext(original_filename)[1]

        return f"{show_name} S{season_num:02d}E{ep_num:02d}{ext}"

    def update_row_preview(self, filename: str, entry_ep: ctk.CTkEntry, lbl_preview: ctk.CTkLabel):
        """Updates the preview label for a single file row."""
        new_name = self.generate_preview_name(filename, entry_ep.get().strip())
        lbl_preview.configure(text=new_name)

    def update_all_previews(self):
        """Refreshes preview labels across all table rows."""
        for filename, entry_ep, lbl_preview in self.file_entries:
            self.update_row_preview(filename, entry_ep, lbl_preview)

    def load_files(self):
        self.folder_path = self.entry_folder.get().strip()

        if not self.folder_path or not os.path.isdir(self.folder_path):
            self.set_status("Warning: Please select or paste a valid directory path.", "orange")
            return

        # Clear existing rows
        for widget in self.table_frame.winfo_children():
            widget.destroy()
        self.file_entries.clear()

        # Headers
        lbl_h1 = ctk.CTkLabel(self.table_frame, text="Current Filename", font=ctk.CTkFont(weight="bold"))
        lbl_h1.grid(row=0, column=0, padx=10, pady=5, sticky="w")
        
        lbl_h2 = ctk.CTkLabel(self.table_frame, text="Episode Number (EXX)", font=ctk.CTkFont(weight="bold"))
        lbl_h2.grid(row=0, column=1, padx=10, pady=5, sticky="w")

        lbl_h3 = ctk.CTkLabel(self.table_frame, text="Preview Filename", font=ctk.CTkFont(weight="bold"))
        lbl_h3.grid(row=0, column=2, padx=10, pady=5, sticky="w")

        self.table_frame.columnconfigure(0, weight=2)
        self.table_frame.columnconfigure(1, weight=1)
        self.table_frame.columnconfigure(2, weight=2)

        # Filter supported video files
        valid_extensions = (".mp4", ".mkv", ".avi", ".mov", ".m4v", ".webm", ".ts")
        files = [f for f in os.listdir(self.folder_path) if f.lower().endswith(valid_extensions)]
        files.sort()

        if not files:
            self.progress_bar.set(0)
            self.set_status("Info: No supported video files found in the selected folder.", "orange")
            return

        # Populate rows with Regex pre-fill and dynamic preview listeners
        for idx, filename in enumerate(files, start=1):
            lbl_file = ctk.CTkLabel(self.table_frame, text=filename, anchor="w")
            lbl_file.grid(row=idx, column=0, padx=10, pady=2, sticky="ew")

            entry_ep = ctk.CTkEntry(self.table_frame, placeholder_text="e.g., 01")
            entry_ep.grid(row=idx, column=1, padx=10, pady=2, sticky="ew")

            lbl_preview = ctk.CTkLabel(self.table_frame, text="-", anchor="w", text_color="gray70")
            lbl_preview.grid(row=idx, column=2, padx=10, pady=2, sticky="ew")

            # Regex auto-detection on load
            detected_ep = self.extract_episode_number(filename)
            if detected_ep:
                entry_ep.insert(0, detected_ep)

            # Bind typing event to update preview dynamically
            entry_ep.bind("<KeyRelease>", lambda event, f=filename, e=entry_ep, p=lbl_preview: self.update_row_preview(f, e, p))

            self.file_entries.append((filename, entry_ep, lbl_preview))

        # Initial preview calculations
        self.update_all_previews()
        self.progress_bar.set(0)
        self.set_status(f"Loaded {len(files)} file(s) from selected directory.")

    def detect_episodes_regex(self):
        """Re-runs Regex extraction across all table rows."""
        if not self.file_entries:
            self.set_status("Warning: No loaded files to scan.", "orange")
            return

        for filename, entry_ep, _ in self.file_entries:
            detected_ep = self.extract_episode_number(filename)
            entry_ep.delete(0, "end")
            if detected_ep:
                entry_ep.insert(0, detected_ep)

        self.update_all_previews()
        self.set_status("Re-scanned episode numbers via Regex.")

    def auto_fill_sequential(self):
        """Sequential 1, 2, 3... fallback fill."""
        if not self.file_entries:
            self.set_status("Warning: No loaded files to fill.", "orange")
            return

        for idx, (_, entry_ep, _) in enumerate(self.file_entries, start=1):
            entry_ep.delete(0, "end")
            entry_ep.insert(0, f"{idx:02d}")

        self.update_all_previews()
        self.set_status("Applied sequential episode numbers.")

    def rename_files(self):
        show_name = self.entry_show_name.get().strip()
        season_str = self.entry_season.get().strip()

        if not show_name:
            self.set_status("Warning: Please enter a Show Name.", "orange")
            return

        if not season_str.isdigit():
            self.set_status("Warning: Please enter a valid numeric Season Number.", "orange")
            return

        season_num = int(season_str)
        rename_history = []
        total_files = len(self.file_entries)

        if total_files == 0:
            self.set_status("Warning: No files loaded to rename.", "orange")
            return

        self.progress_bar.set(0)

        for idx, (original_name, ep_entry, _) in enumerate(self.file_entries, start=1):
            ep_str = ep_entry.get().strip()
            if not ep_str:
                self.progress_bar.set(idx / total_files)
                continue  # Skip files without an assigned episode number

            if not ep_str.isdigit():
                self.set_status(f"Error: Invalid episode number '{ep_str}' for file '{original_name}'.", "#ff4d4d")
                return

            ep_num = int(ep_str)
            ext = os.path.splitext(original_name)[1]
            
            # Format: <Show_name> SXXEXX.ext
            new_name = f"{show_name} S{season_num:02d}E{ep_num:02d}{ext}"
            
            old_full_path = os.path.join(self.folder_path, original_name)
            new_full_path = os.path.join(self.folder_path, new_name)

            if old_full_path != new_full_path:
                try:
                    os.rename(old_full_path, new_full_path)
                    rename_history.append((old_full_path, new_full_path))
                except Exception as e:
                    self.set_status(f"Error renaming '{original_name}': {e}", "#ff4d4d")
                    break

            self.progress_bar.set(idx / total_files)
            self.update_idletasks()

        if rename_history:
            self.last_rename_history = rename_history
            self.btn_undo.configure(state="normal")
            self.set_status(f"Success: Successfully renamed {len(rename_history)} file(s)!", "#2fa572")
            self.load_files()  # Refresh table after renaming

    def undo_rename(self):
        if not self.last_rename_history:
            self.set_status("Warning: No rename history available to undo.", "orange")
            return

        reverted_count = 0
        failed_count = 0
        total_items = len(self.last_rename_history)

        self.progress_bar.set(0)

        # Roll back in reverse order of execution
        for idx, (old_full_path, new_full_path) in enumerate(reversed(self.last_rename_history), start=1):
            if not os.path.exists(new_full_path) or (os.path.exists(old_full_path) and old_full_path != new_full_path):
                failed_count += 1
            else:
                try:
                    os.rename(new_full_path, old_full_path)
                    reverted_count += 1
                except Exception:
                    failed_count += 1

            self.progress_bar.set(idx / total_items)
            self.update_idletasks()

        self.last_rename_history.clear()
        self.btn_undo.configure(state="disabled")

        if failed_count > 0:
            self.set_status(f"Rollback Complete: Reverted {reverted_count} file(s). Failed {failed_count} file(s).", "orange")
        else:
            self.set_status(f"Rollback Complete: Reverted {reverted_count} file(s) to original names!", "#2fa572")

        self.load_files()

if __name__ == "__main__":
    app = EpisodeRenamer()
    app.mainloop()