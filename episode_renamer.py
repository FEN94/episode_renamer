import os
import re
import customtkinter as ctk
from tkinter import filedialog, messagebox

ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")

class EpisodeRenamer(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Episode Renamer")
        self.geometry("950x620")

        self.folder_path = ""
        self.file_entries = []  # Stores (original_filename, CTkEntry, CTkLabel_Preview) tuples

        # --- Top Control Panel ---
        self.top_frame = ctk.CTkFrame(self)
        self.top_frame.pack(pady=10, padx=10, fill="x")

        self.btn_select_folder = ctk.CTkButton(self.top_frame, text="Select Folder", command=self.select_folder)
        self.btn_select_folder.grid(row=0, column=0, padx=5, pady=5)

        self.entry_folder = ctk.CTkEntry(self.top_frame, placeholder_text="No folder selected")
        self.entry_folder.grid(row=0, column=1, columnspan=3, padx=5, pady=5, sticky="ew")

        # Show Name Input
        ctk.CTkLabel(self.top_frame, text="Show Name:").grid(row=1, column=0, padx=5, pady=5, sticky="e")
        self.entry_show_name = ctk.CTkEntry(self.top_frame, placeholder_text="e.g., Breaking Bad")
        self.entry_show_name.grid(row=1, column=1, padx=5, pady=5, sticky="ew")
        self.entry_show_name.bind("<KeyRelease>", lambda event: self.update_all_previews())

        # Season Input
        ctk.CTkLabel(self.top_frame, text="Season Number:").grid(row=1, column=2, padx=5, pady=5, sticky="e")
        self.entry_season = ctk.CTkEntry(self.top_frame, placeholder_text="e.g., 1")
        self.entry_season.grid(row=1, column=3, padx=5, pady=5, sticky="ew")
        self.entry_season.bind("<KeyRelease>", lambda event: self.update_all_previews())

        self.top_frame.columnconfigure(1, weight=1)
        self.top_frame.columnconfigure(3, weight=1)

        # Action Buttons
        self.btn_load = ctk.CTkButton(self.top_frame, text="Load Files", command=self.load_files)
        self.btn_load.grid(row=2, column=0, padx=5, pady=10, sticky="ew")

        self.btn_detect_regex = ctk.CTkButton(self.top_frame, text="Detect EP via Regex", command=self.detect_episodes_regex)
        self.btn_detect_regex.grid(row=2, column=1, padx=5, pady=10, sticky="ew")

        self.btn_autofill = ctk.CTkButton(self.top_frame, text="Sequential Fill", command=self.auto_fill_sequential)
        self.btn_autofill.grid(row=2, column=2, padx=5, pady=10, sticky="ew")

        self.btn_rename = ctk.CTkButton(self.top_frame, text="Start Rename", fg_color="green", hover_color="darkgreen", command=self.rename_files)
        self.btn_rename.grid(row=2, column=3, padx=5, pady=10, sticky="ew")

        # --- Table / Scrollable Frame Panel ---
        self.table_frame = ctk.CTkScrollableFrame(self, label_text="Files")
        self.table_frame.pack(pady=10, padx=10, fill="both", expand=True)

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
            messagebox.showwarning("Warning", "Please select or paste a valid directory path.")
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
            messagebox.showinfo("Info", "No video files (.mp4, .mkv, .avi, .mov, .m4v, .webm, .ts) found in the selected folder.")
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

    def detect_episodes_regex(self):
        """Re-runs Regex extraction across all table rows."""
        if not self.file_entries:
            messagebox.showwarning("Warning", "No loaded files to scan.")
            return

        for filename, entry_ep, _ in self.file_entries:
            detected_ep = self.extract_episode_number(filename)
            entry_ep.delete(0, "end")
            if detected_ep:
                entry_ep.insert(0, detected_ep)

        self.update_all_previews()

    def auto_fill_sequential(self):
        """Sequential 1, 2, 3... fallback fill."""
        if not self.file_entries:
            messagebox.showwarning("Warning", "No loaded files to fill.")
            return

        for idx, (_, entry_ep, _) in enumerate(self.file_entries, start=1):
            entry_ep.delete(0, "end")
            entry_ep.insert(0, f"{idx:02d}")

        self.update_all_previews()

    def rename_files(self):
        show_name = self.entry_show_name.get().strip()
        season_str = self.entry_season.get().strip()

        if not show_name:
            messagebox.showwarning("Warning", "Please enter a Show Name.")
            return

        if not season_str.isdigit():
            messagebox.showwarning("Warning", "Please enter a valid numeric Season Number.")
            return

        season_num = int(season_str)
        renamed_count = 0

        for original_name, ep_entry, _ in self.file_entries:
            ep_str = ep_entry.get().strip()
            if not ep_str:
                continue  # Skip files without an assigned episode number

            if not ep_str.isdigit():
                messagebox.showerror("Error", f"Invalid episode number '{ep_str}' for file {original_name}.")
                return

            ep_num = int(ep_str)
            ext = os.path.splitext(original_name)[1]
            
            # Format: <Show_name> SXXEXX.ext
            new_name = f"{show_name} S{season_num:02d}E{ep_num:02d}{ext}"
            
            old_full_path = os.path.join(self.folder_path, original_name)
            new_full_path = os.path.join(self.folder_path, new_name)

            if old_full_path == new_full_path:
                continue

            try:
                os.rename(old_full_path, new_full_path)
                renamed_count += 1
            except Exception as e:
                messagebox.showerror("Error", f"Failed to rename {original_name}:\n{e}")
                return

        messagebox.showinfo("Success", f"Successfully renamed {renamed_count} file(s)!")
        self.load_files()  # Refresh table after renaming

if __name__ == "__main__":
    app = EpisodeRenamer()
    app.mainloop()