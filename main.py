import tkinter as tk
from tkinter import filedialog, messagebox
import yt_dlp
import os
from pathlib import Path
import threading


def browse_folder():
    """Opens a dialog to select a download directory."""
    folder_selected = filedialog.askdirectory(initialdir=path_var.get())
    if folder_selected:
        path_var.set(folder_selected)


def download_video(resolution):
    """Handles the download process in a separate thread to keep the GUI responsive."""
    url = url_var.get()
    save_path = path_var.get()

    if not url.strip():
        messagebox.showwarning("Input Error", "Please enter a valid YouTube link.")
        return

    # Update status
    status_var.set(f"Downloading in {resolution}... Please wait.")
    disable_buttons()

    def run_download():
        # Set the download format based on the button clicked
        if resolution == "1080p":
            format_code = 'bestvideo[height<=1080]+bestaudio/best[height<=1080]/best'
        elif resolution == "720p":
            format_code = 'bestvideo[height<=720]+bestaudio/best[height<=720]/best'
        else:  # 480p
            format_code = 'bestvideo[height<=480]+bestaudio/best[height<=480]/best'

        ydl_opts = {
            'format': format_code,
            'outtmpl': os.path.join(save_path, '%(title)s.%(ext)s'),
            'merge_output_format': 'mp4',
            'quiet': True,
            'no_warnings': True,
            'nocheckcertificate': True  # <-- Add this line here
        }

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
            # Use root.after to safely interact with the GUI from a background thread
            root.after(0, lambda: messagebox.showinfo("Success", "Video downloaded successfully!"))
            root.after(0, lambda: status_var.set("Ready"))
        except Exception as e:
            root.after(0, lambda: messagebox.showerror("Error", f"An error occurred:\n{str(e)}"))
            root.after(0, lambda: status_var.set("Ready"))
        finally:
            root.after(0, enable_buttons)

    # Start the download in a background thread
    threading.Thread(target=run_download, daemon=True).start()


def disable_buttons():
    btn_1080.config(state="disabled")
    btn_720.config(state="disabled")
    btn_480.config(state="disabled")


def enable_buttons():
    btn_1080.config(state="normal")
    btn_720.config(state="normal")
    btn_480.config(state="normal")


# --- GUI Setup ---
root = tk.Tk()
root.title("YouTube Video Downloader")
root.geometry("500x300")
root.resizable(False, False)

# Variables
url_var = tk.StringVar()
path_var = tk.StringVar(value=str(Path.home() / "Downloads"))  # Defaults to OS Downloads folder
status_var = tk.StringVar(value="Ready")

# --- Layout ---

# URL Input
tk.Label(root, text="YouTube Link:", font=("Arial", 10, "bold")).pack(pady=(20, 5))
url_entry = tk.Entry(root, textvariable=url_var, width=55)
url_entry.pack()

# Path Selection
tk.Label(root, text="Save to:", font=("Arial", 10, "bold")).pack(pady=(15, 5))
path_frame = tk.Frame(root)
path_frame.pack()

path_entry = tk.Entry(path_frame, textvariable=path_var, width=42, state="readonly")
path_entry.pack(side=tk.LEFT, padx=(0, 10))

browse_btn = tk.Button(path_frame, text="Browse", command=browse_folder)
browse_btn.pack(side=tk.LEFT)

# Resolution Buttons
tk.Label(root, text="Select Resolution to Download:", font=("Arial", 10, "bold")).pack(pady=(20, 5))
btn_frame = tk.Frame(root)
btn_frame.pack()

btn_1080 = tk.Button(btn_frame, text="Download 1080p", bg="#ffcccc", command=lambda: download_video("1080p"))
btn_1080.pack(side=tk.LEFT, padx=5)

btn_720 = tk.Button(btn_frame, text="Download 720p", bg="#ccffcc", command=lambda: download_video("720p"))
btn_720.pack(side=tk.LEFT, padx=5)

btn_480 = tk.Button(btn_frame, text="Download 480p", bg="#ccccff", command=lambda: download_video("480p"))
btn_480.pack(side=tk.LEFT, padx=5)

# Status Label
status_label = tk.Label(root, textvariable=status_var, fg="gray", font=("Arial", 9, "italic"))
status_label.pack(side=tk.BOTTOM, pady=15)

# Start Application
root.mainloop()