import sys
import tkinter as tk
from tkinter import filedialog, messagebox
import customtkinter as ctk  # <-- The UI Upgrade!
import yt_dlp
import os
from pathlib import Path
import threading

# --- Core Functions ---
def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)
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
            'nocheckcertificate': True,
            'progress_hooks': [progress_hook],
            'ffmpeg_location': resource_path('ffmpeg')  # <-- ADD THIS LINE!
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
            root.after(0, lambda: url_entry.delete(0, tk.END))

    threading.Thread(target=run_download, daemon=True).start()

def disable_buttons():
    # Note: customtkinter uses .configure() instead of .config()
    btn_1440.configure(state="disabled")
    btn_1080.configure(state="disabled")
    btn_720.configure(state="disabled")

def enable_buttons():
    btn_1440.configure(state="normal")
    btn_1080.configure(state="normal")
    btn_720.configure(state="normal")

# --- GUI Setup & Styling ---

# Force light mode globally for CustomTkinter
ctk.set_appearance_mode("light")

root = ctk.CTk()
root.title("Youtubology")
root.geometry("550x380") # Made slightly taller to accommodate the new borders
root.resizable(False, False)
# CustomTkinter automatically sets the background to a clean white in light mode

# Variables
url_var = tk.StringVar()
path_var = tk.StringVar(value=str(Path.home() / "Downloads"))
status_var = tk.StringVar(value="Ready to download")

# --- Layout ---

# Application Title
title_label = ctk.CTkLabel(root, text="Y O U T U B O L O G Y", font=("Courier", 26, "bold"), text_color="#FF0000")
title_label.pack(pady=(20, 15))

# URL Input
ctk.CTkLabel(root, text="YouTube Link:", font=("Arial", 12, "bold"), text_color="#000000").pack(pady=(5, 2))
url_entry = ctk.CTkEntry(root, textvariable=url_var, width=450, font=("Arial", 12), border_color="#000000", border_width=2, fg_color="#FFFFFF", text_color="#000000")
url_entry.pack()

# Path Selection
ctk.CTkLabel(root, text="Save Destination:", font=("Arial", 12, "bold"), text_color="#000000").pack(pady=(15, 2))
path_frame = ctk.CTkFrame(root, fg_color="transparent")
path_frame.pack()

path_entry = ctk.CTkEntry(path_frame, textvariable=path_var, width=350, font=("Arial", 12), state="readonly", fg_color="#F0F0F0", text_color="#000000")
path_entry.pack(side=tk.LEFT, padx=(0, 10))

browse_btn = ctk.CTkButton(path_frame, text="Browse", command=browse_folder, fg_color="#000000", text_color="#FFFFFF", hover_color="#333333", width=80, corner_radius=8, font=("Arial", 12, "bold"))
browse_btn.pack(side=tk.LEFT)

# Resolution Buttons
ctk.CTkLabel(root, text="Select Resolution:", font=("Arial", 12, "bold"), text_color="#FF0000").pack(pady=(20, 5))
btn_frame = ctk.CTkFrame(root, fg_color="transparent")
btn_frame.pack()

# The corner_radius attribute makes them completely rounded!
btn_1440 = ctk.CTkButton(btn_frame, text="1440p (2K)", command=lambda: download_video("1440p"), fg_color="#FF0000", text_color="#FFFFFF", hover_color="#CC0000", corner_radius=20, width=120, font=("Arial", 12, "bold"))
btn_1440.pack(side=tk.LEFT, padx=10)

btn_1080 = ctk.CTkButton(btn_frame, text="1080p (HD)", command=lambda: download_video("1080p"), fg_color="#FF0000", text_color="#FFFFFF", hover_color="#CC0000", corner_radius=20, width=120, font=("Arial", 12, "bold"))
btn_1080.pack(side=tk.LEFT, padx=10)

btn_720 = ctk.CTkButton(btn_frame, text="720p", command=lambda: download_video("720p"), fg_color="#FF0000", text_color="#FFFFFF", hover_color="#CC0000", corner_radius=20, width=120, font=("Arial", 12, "bold"))
btn_720.pack(side=tk.LEFT, padx=10)

# Status Label (Live Progress)
status_label = ctk.CTkLabel(root, textvariable=status_var, font=("Courier", 12), text_color="#FF0000")
status_label.pack(side=tk.BOTTOM, pady=20)

# Start Application
root.mainloop()