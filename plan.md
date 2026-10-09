# Episode renamer

## 1. Objective
Create a python app that rename multiple files for episodes of shows.

## 2. In-Scope:
- Take folder path of the episodes that are going to be renamed.
- folder path field must be editable.
- Button to load the files into a tables
- Take the show name as a entry and season.
- Show in the table two columns. One that shows the current files names, the other is an editable columns to put the episode number.
- Load on the table mp4, mkv, avi, mov, m4v, webm and ts files.
- Regex auto-detection for episode numbers.
- Button to start the rename process.
- Add preview column to show the new Filename before the rename process.
- Undo/rollback option in case of any mistake
- add status bar/progress indicator when the rename process start.

## 3. File naming
- "<Show_name> <SXXEXX>" (without quotes) where **show_name** is the name of the show, **SXX** is the season of the show, and **EXX** is the episode.

## 4. Key Decisions (ADRs)
- **Language:** Python
- **Architecture:** None
- **GUI Framework:** Customtkinter
- **Data Storage:** None

