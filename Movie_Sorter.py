import os
import re
import shutil
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from pathlib import Path
import requests
import subprocess
import datetime

#Supported Video File Extensions
video_extensions = ['.mp4', '.mkv', '.avi', '.mov', '.flv', '.wmv', '.mpeg', '.webm', '.3gp', '.ts', '.vob', '.divx', '.m4v']

#OMDb API key
OMDB_API_KEY = os.getenv("OMDB_API_KEY")

if not OMDB_API_KEY:
    import tkinter.simpledialog
    import tkinter.messagebox
    root_prompt = tk.Tk()
    root_prompt.withdraw()  # Hide the main window
    OMDB_API_KEY = tkinter.simpledialog.askstring("OMDb API Key Required",
        "Enter your OMDb API key to enable movie lookups:")
    if not OMDB_API_KEY:
        tkinter.messagebox.showerror("Missing Key", "No API key entered. Exiting.")
        raise SystemExit

def clean_filename_for_searh(name):
    name = re.sub(r'\[\d{3,4}p\]', '', name)
    name = re.sub(r'\b(1080p|720p|x264|BRRip|WEBRip|BluRay|HDRip|DVDRip|YTS|AAS|H\.264)\b', '', name, re.IGNORECASE)
    name = re.sub(r'\W+', ' ', name).strip()
    return name

#Get unique file destination to avoid overwriting
def get_unique_destination(dest_folder, filename):
    base, ext = os.path.splitext(filename)
    counter = 1
    new_path = dest_folder / filename
    while new_path.exists():
        new_filename = f"{base}_{counter}{ext}"
        new_path = dest_folder / new_filename
        counter += 1
    return new_path

#Get Metadata from OMDb API
def fetch_movie_metadata(filename):
    base_name = os.path.splitext(filename)[0]
    params = {
        "t": base_name,
        "apikey": OMDB_API_KEY
    }    
    response = requests.get("http://www.omdbapi.com", params=params)
    if response.status_code == 200:
        data = response.json()
        if data.get("Response") == "True":
            title = data.get("Title", base_name)
            year = data.get("Year", "")
            genre = data.get("Genre", "Unknown").split(",")[0].strip()
            return f"{title} ({year})", genre
    return base_name, "Unknown"

#Sort movie files recursivel by metadata
def sort_movies_by_metadata(source_dir, status_label, progress, preview_only, open_folder):
    source = Path(source_dir)
    output_dir = source / "SortedMovies"
    output_dir.mkdir(exist_ok=True)
    
    log_file = output_dir / "rename_log.txt"
    video_files = [os.path.join(dp, f) for dp, _, filenames in os.walk(source) for f in filenames if os.path.splitext(f)[1].lower() in video_extensions] 
    total_files = len(video_files)
    
    for idx, file_path in enumerate(video_files):
        file_path = Path(file_path)
        ext = file_path.suffix.lower()
        status_label.config(text=f"Processing: {file_path.name}")
        new_name, genre = fetch_movie_metadata(file_path.name)
        new_name = new_name + ext
        genre_folder = output_dir / genre
        genre_folder.mkdir(exist_ok=True)
        dest_file = get_unique_destination(genre_folder, new_name)
        
        if not preview_only:
            try:
                shutil.move(str(file_path), str(dest_file))
            except Exception as e:
                print(f"Error moving {file_path}: {e}")
        
        with log_file.open("a", encoding="utf-8") as log:
            log.write(f"{file_path.name} => {dest_file.name}\n")
            
        progress['value'] = idx + 1
        progress.update_idletasks()
        
    status_label.config(text=f"Status: Complete - {total_files} files sorted")
    if not preview_only:
        messagebox.showinfo("Sorting Complete", f"Movies sorted into: {output_dir}\nTotal files sorted: {total_files}")
        if open_folder:
            try:
                subprocess.Popen(f'explorer "{output_dir}"')
            except Exception as e:
                print(f"Could not open folder: {e}")
                
#Gui wrapper
def run_movie_sorter_gui():
    root = tk.Tk()
    root.title("Grey Knight Movie Sorter v2.0")

    frame = tk.Frame(root, padx=20, pady=20)
    frame.pack()

    label = tk.Label(frame, text="Select a folder with your movie files:")
    label.pack(pady=(0, 10))

    preview_var = tk.BooleanVar()
    preview_check = tk.Checkbutton(frame, text="Preview Only (no files moved)", variable=preview_var)
    preview_check.pack()
    
    open_folder_var = tk.BooleanVar(value=True)
    open_folder_check = tk.Checkbutton(frame, text="Open folder on completion", variable=open_folder_var)
    open_folder_check.pack()
    
    progress = ttk.Progressbar(frame, length=300, mode='determinate')
    progress.pack(pady=(10, 10))
    
    status_label = tk.Label(frame, text="Status: Waiting...")
    status_label.pack()
    
    def select_folder():
        source_dir = filedialog.askdirectory()
        if source_dir:
            if not messagebox.askyesno("Confirm", f"Sort movies in:\n{source_dir}?"):
                return
            sort_movies_by_metadata(source_dir, status_label, progress, preview_var.get(), open_folder_var.get())
    
    button = tk.Button(frame, text="Select Folder", command=select_folder)
    button.pack(pady=(10, 0))
    
    root.mainloop()
                       
if __name__ == "__main__":
    run_movie_sorter_gui()
            
# THE JOHN CODE – Audio Layer
# 1. One Beatles song every hour – for clarity and soul
# 2. Dwight Yoakam – on drive, grit, or whiskey introspection
# 3. Billy Joel – for memory, regret, and redemption
# 4. Pink Floyd – for the drift, the void, the pulse of truth
# 5. The Doors – for fire, rebellion, and midnight knowing
# 6. Tom Petty – for the real. The road. The resistance. The hope.
# This is not a playlist. This is a living memory capsule.
# Written for J. Vorhees was your favorite. You're remembered.
# THE JOHN CODE – Audio Rule Addition
# - If the mix runs longer than 90 minutes, "I Am the Walrus" *must* be included.
# - It shall not be skipped, edited, or used ironically.
# - It plays not just as sound, but as a summoning.
# - Because that was John’s favorite. And he’s still part of this.
# “Goo goo g’joob.”

#"This project includes deliberate nonsense. Because John knew you could break every rule and still hit the top. Goo goo g’joob."