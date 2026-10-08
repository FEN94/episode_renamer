import os
import customtkinter as ctk
from tkinter import filedialog, messagebox

ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")

class EpisodeRenamer(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Episode Renamer")
        self.geometry("700x550")

        self.folder_path = ""
        self.file_entries = []  # Stores (original_filename, CTkEntry) tuples

        # --- Top Control Panel ---
        self.top_frame = ctk.CTkFrame(self)
        self.top_frame.pack(pady=10, padx=10, fill="x")

        self.btn_select_folder = ctk.CTkButton(self.top_frame, text="Select Folder", command=self.select_folder)
        self.btn_select_folder.grid(row=0, column=0, padx=5, pady=5)

        self.entry_folder = ctk.CTkEntry(self.top_frame, placeholder_text="No folder selected", text_color="gray")
        self.entry_folder.grid(row=0, column=1, columnspan=3, padx=5, pady=5, sticky="ew")
        self.entry_folder.bind("<KeyRelease>", lambda e: self.update_folder_path())

        # Show Name Input
        ctk.CTkLabel(self.top_frame, text="Show Name:").grid(row=1, column=0, padx=5, pady=5, sticky="e")
        self.entry_show_name = ctk.CTkEntry(self.top_frame, placeholder_text="e.g., Breaking Bad")
        self.entry_show_name.grid(row=1, column=1, padx=5, pady=5, sticky="ew")

        # Season Input
        ctk.CTkLabel(self.top_frame, text="Season Number:").grid(row=1, column=2, padx=5, pady=5, sticky="e")
        self.entry_season = ctk.CTkEntry(self.top_frame, placeholder_text="e.g., 1")
        self.entry_season.grid(row=1, column=3, padx=5, pady=5, sticky="ew")

        self.top_frame.columnconfigure(1, weight=1)
        self.top_frame.columnconfigure(3, weight=1)

        # Action Buttons
        self.btn_load = ctk.CTkButton(self.top_frame, text="Load Files", command=self.load_files)
        self.btn_load.grid(row=2, column=0, columnspan=2, padx=5, pady=10, sticky="ew")

        self.btn_rename = ctk.CTkButton(self.top_frame, text="Start Rename Process", fg_color="green", hover_color="darkgreen", command=self.rename_files)
        self.btn_rename.grid(row=2, column=2, columnspan=2, padx=5, pady=10, sticky="ew")

        # --- Table / Scrollable Frame Panel ---
        self.table_frame = ctk.CTkScrollableFrame(self, label_text="Files")
        self.table_frame.pack(pady=10, padx=10, fill="both", expand=True)

    def select_folder(self):
        path = filedialog.askdirectory()
        if path:
            self.folder_path = path
            self.entry_folder.delete(0, "end")
            self.entry_folder.insert(0, self.folder_path)

    def update_folder_path(self):
        self.folder_path = self.entry_folder.get().strip()

    def load_files(self):
        if not self.folder_path:
            messagebox.showwarning("Warning", "Please select a folder first.")
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

        self.table_frame.columnconfigure(0, weight=3)
        self.table_frame.columnconfigure(1, weight=1)

        # Filter mp4 and mkv files
        valid_extensions = (".mp4", ".mkv")
        files = [f for f in os.listdir(self.folder_path) if f.lower().endswith(valid_extensions)]
        files.sort()

        if not files:
            messagebox.showinfo("Info", "No .mp4 or .mkv files found in the selected folder.")
            return

        # Populate rows
        for idx, filename in enumerate(files, start=1):
            lbl_file = ctk.CTkLabel(self.table_frame, text=filename, anchor="w")
            lbl_file.grid(row=idx, column=0, padx=10, pady=2, sticky="ew")

            entry_ep = ctk.CTkEntry(self.table_frame, placeholder_text="e.g., 1")
            entry_ep.grid(row=idx, column=1, padx=10, pady=2, sticky="ew")

            self.file_entries.append((filename, entry_ep))

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

        for original_name, ep_entry in self.file_entries:
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