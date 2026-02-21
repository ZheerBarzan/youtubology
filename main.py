import tkinter as tk
from tkinter import filedialog, messagebox
import yt_dlp
import os
from pathlib import Path
import threading


# --- Core Functions ---

def browse_folder():
    """Opens a dialog to select a download directory."""
    folder_selected = filedialog.askdirectory(initialdir=path_var.get())
    if folder_selected:
        path_var.set(folder_selected)


def progress_hook(d):
    """Hooks into yt-dlp to get live download progress."""
    if d['status'] == 'downloading':
        percent = d.get('_percent_str', '0.0%').strip()
        speed = d.get('_speed_str', '0KiB/s').strip()
        # Safely update the GUI from the background thread
        root.after(0, lambda: status_var.set(f"Downloading: {percent} (Speed: {speed})"))
    elif d['status'] == 'finished':
        root.after(0, lambda: status_var.set("Download complete! Processing audio/video..."))


def download_video(resolution):
    """Handles the download process in a separate thread."""
    url = url_var.get()
    save_path = path_var.get()

    if not url.strip():
        messagebox.showwarning("Input Error", "Please enter a valid YouTube link.")
        return

    disable_buttons()
    status_var.set("Connecting to YouTube...")

    def run_download():
        # Set format based on the selected resolution
        if resolution == "1440p":
            format_code = 'bestvideo[height<=1440]+bestaudio/best[height<=1440]/best'
        elif resolution == "1080p":
            format_code = 'bestvideo[height<=1080]+bestaudio/best[height<=1080]/best'
        else:  # 720p
            format_code = 'bestvideo[height<=720]+bestaudio/best[height<=720]/best'

        ydl_opts = {
            'format': format_code,
            'outtmpl': os.path.join(save_path, '%(title)s.%(ext)s'),
            'merge_output_format': 'mp4',
            'quiet': True,
            'no_warnings': True,
            'nocheckcertificate': True,  # Keeping your SSL fix active!
            'progress_hooks': [progress_hook]  # Connects our live status updater
        }

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
            root.after(0, lambda: messagebox.showinfo("Success", "Video successfully downloaded!"))
            root.after(0, lambda: status_var.set("Ready for next download."))
        except Exception as e:
            root.after(0, lambda: messagebox.showerror("Error", f"An error occurred:\n{str(e)}"))
            root.after(0, lambda: status_var.set("Error occurred. Ready."))
        finally:
            root.after(0, enable_buttons)
            root.after(0, lambda: url_entry.delete(0, tk.END))  # Clear the URL field automatically

    # Start the download in a background thread
    threading.Thread(target=run_download, daemon=True).start()


def disable_buttons():
    btn_1440.config(state="disabled")
    btn_1080.config(state="disabled")
    btn_720.config(state="disabled")


def enable_buttons():
    btn_1440.config(state="normal")
    btn_1080.config(state="normal")
    btn_720.config(state="normal")


# --- GUI Setup & Styling ---

root = tk.Tk()
root.title("Youtubology")
root.geometry("550x350")
root.resizable(False, False)
root.config(bg="#FFFFFF")  # White Mode Background

# Variables
url_var = tk.StringVar()
path_var = tk.StringVar(value=str(Path.home() / "Downloads"))
status_var = tk.StringVar(value="Ready to download")

# Button styling dictionaries to keep code clean
btn_style = {
    "bg": "#FF0000",  # YouTube Red
    "fg": "#FFFFFF",  # White text
    "font": ("Arial", 10, "bold"),
    "relief": "flat",  # Modern flat look
    "padx": 10,
    "pady": 5
}

# --- Layout ---

# Application Title
title_label = tk.Label(root, text="Y O U T U B O L O G Y", font=("Courier", 22, "bold"), bg="#FFFFFF", fg="#ff0000")
title_label.pack(pady=(20, 15))

# URL Input
tk.Label(root, text="YouTube Link:", font=("Arial", 10, "bold"), bg="#FFFFFF", fg='#000000').pack(pady=(10, 2))
url_entry = tk.Entry(root, textvariable=url_var, width=60, font=("Arial", 10), highlightthickness=2,
                     highlightbackground="#000000", background="#FFFFFF", foreground="#000000")
url_entry.pack(ipady=3)  # ipady makes the text box a little taller

# Path Selection
tk.Label(root, text="Save Destination:", font=("Arial", 10, "bold"), bg="#FFFFFF", fg="black").pack(pady=(15, 2))
path_frame = tk.Frame(root, bg="#FFFFFF")
path_frame.pack()

path_entry = tk.Entry(path_frame, textvariable=path_var, width=45, state="readonly", font=("Arial", 10))
path_entry.pack(side=tk.LEFT, padx=(0, 10), ipady=3)

browse_btn = tk.Button(path_frame, text="Browse", command=browse_folder, bg="#ffffff", fg="black")
browse_btn.pack(side=tk.LEFT)

# Resolution Buttons
tk.Label(root, text="Select Resolution:", font=("Arial", 10, "bold"), bg="#FFffff",fg="#ff0000").pack(pady=(20, 5))
btn_frame = tk.Frame(root, bg="#FFFFFF")
btn_frame.pack()

btn_1440 = tk.Button(btn_frame, text="1440p (2K)", command=lambda: download_video("1440p"), **btn_style)
btn_1440.pack(side=tk.LEFT, padx=10)

btn_1080 = tk.Button(btn_frame, text="1080p (HD)", command=lambda: download_video("1080p"), **btn_style)
btn_1080.pack(side=tk.LEFT, padx=10)

btn_720 = tk.Button(btn_frame, text="720p", command=lambda: download_video("720p"), **btn_style)
btn_720.pack(side=tk.LEFT, padx=10)

# Status Label (Live Progress)
status_label = tk.Label(root, textvariable=status_var, font=("Courier", 10), bg="#FFFFFF", fg="#FF0000")
status_label.pack(side=tk.BOTTOM, pady=20)

# Start Application
root.mainloop()