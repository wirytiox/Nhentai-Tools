import os
import zipfile
import tkinter as tk
from tkinter import filedialog, messagebox
import re
import sys
import threading
import queue

# Function to shorten or sanitize folder names if needed
def sanitize_folder_name(folder_name):
    # Remove special characters (except spaces and alphanumeric) and limit length to 200 chars
    sanitized_name = re.sub(r'[^a-zA-Z0-9 \-_]', '', folder_name)
    return sanitized_name[:200]

# Function to create the CBZ file from nested folders
def create_cbz_from_nested_folder(input_folder, output_folder, log_queue):
    if not os.path.exists(input_folder):
        log_queue.put("Input folder does not exist.\n")
        return

    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    # Traverse one folder deep inside the input folder
    for subfolder in os.listdir(input_folder):
        subfolder_path = os.path.join(input_folder, subfolder)

        if os.path.isdir(subfolder_path):
            # Check if CBZ file already exists
            cbz_filename = os.path.join(output_folder, f"{subfolder}.cbz")
            if os.path.exists(cbz_filename):
                log_queue.put(f"CBZ file already exists for '{subfolder}', skipping conversion.\n")
                continue

            image_files = sorted([f for f in os.listdir(subfolder_path) if f.lower().endswith(('.png', '.jpg', '.jpeg', '.gif'))])

            if not image_files:
                log_queue.put(f"No images found in the folder: {subfolder}\n")
                continue

            first_image = image_files[0]
            last_image = image_files[-1]
            log_queue.put(f"Processing '{subfolder}'\n")
            log_queue.put(f"First image: {first_image}\n")
            log_queue.put(f"Last image: {last_image}\n")

            try:
                # Try creating the CBZ file
                with zipfile.ZipFile(cbz_filename, 'w') as cbz:
                    for image in image_files:
                        image_path = os.path.join(subfolder_path, image)
                        cbz.write(image_path, arcname=image)

                log_queue.put(f"CBZ file created: {cbz_filename}\n")
            except Exception as e:
                log_queue.put(f"Error saving CBZ file: {e}\n")
                # Retry with sanitized folder name
                safe_folder_name = sanitize_folder_name(subfolder)
                safe_cbz_filename = os.path.join(output_folder, f"{safe_folder_name}.cbz")

                if os.path.exists(safe_cbz_filename):
                    log_queue.put(f"Sanitized CBZ file already exists for '{safe_folder_name}', skipping conversion.\n")
                    continue

                try:
                    with zipfile.ZipFile(safe_cbz_filename, 'w') as cbz:
                        for image in image_files:
                            image_path = os.path.join(subfolder_path, image)
                            cbz.write(image_path, arcname=image)
                    log_queue.put(f"CBZ file created: {safe_cbz_filename}\n")
                except Exception as e2:
                    log_queue.put(f"Failed again with sanitized folder name: {e2}\n")

    log_queue.put("CBZ files have been created successfully!\n")

# Function to open a folder dialog and return the selected path
def select_folder(var):
    folder_selected = filedialog.askdirectory()
    if folder_selected:
        var.set(folder_selected)

# Function to start the conversion process (running in a separate thread)
def start_conversion_thread(input_var, output_var, log_queue):
    input_folder = input_var.get()
    output_folder = output_var.get()

    if not input_folder or not output_folder:
        messagebox.showerror("Error", "Please select both input and output directories.")
        return

    log_queue.put("Starting conversion...\n")
    create_cbz_from_nested_folder(input_folder, output_folder, log_queue)

# Function to display logs in the text widget
def display_logs(log_queue, log_text):
    while not log_queue.empty():
        log_message = log_queue.get_nowait()
        log_text.insert(tk.END, log_message)
        log_text.see(tk.END)  # Auto-scroll to the bottom

    # Call this function again after 100 ms to check for new logs
    log_text.after(100, display_logs, log_queue, log_text)

# Main function to create the GUI
def create_gui():
    root = tk.Tk()
    root.title("Manga to CBZ Converter")
    root.geometry("700x400")  # Make the window resizable

    # Variables to store folder paths
    input_var = tk.StringVar()
    output_var = tk.StringVar()

    # Create a queue for log messages
    log_queue = queue.Queue()

    # Input folder selection
    tk.Label(root, text="Input Directory:").grid(row=0, column=0, padx=10, pady=5, sticky='e')
    tk.Entry(root, textvariable=input_var, width=50).grid(row=0, column=1, padx=10, pady=5)
    tk.Button(root, text="Browse", command=lambda: select_folder(input_var)).grid(row=0, column=2, padx=10, pady=5)

    # Output folder selection
    tk.Label(root, text="Output Directory:").grid(row=1, column=0, padx=10, pady=5, sticky='e')
    tk.Entry(root, textvariable=output_var, width=50).grid(row=1, column=1, padx=10, pady=5)
    tk.Button(root, text="Browse", command=lambda: select_folder(output_var)).grid(row=1, column=2, padx=10, pady=5)

    # Start button
    tk.Button(root, text="Start Conversion", command=lambda: threading.Thread(target=start_conversion_thread, args=(input_var, output_var, log_queue)).start()).grid(row=2, column=0, columnspan=3, padx=10, pady=10)

    # Text widget to show logs
    log_text = tk.Text(root, height=15, width=80)
    log_text.grid(row=3, column=0, columnspan=3, padx=10, pady=10, sticky="nsew")

    # Add a scrollbar to the text widget
    scrollbar = tk.Scrollbar(root, command=log_text.yview)
    scrollbar.grid(row=3, column=3, sticky='nsew')
    log_text.config(yscrollcommand=scrollbar.set)

    # Resize behavior
    root.grid_rowconfigure(3, weight=1)  # Allow the text box row to expand
    root.grid_columnconfigure(1, weight=1)  # Allow the middle column to expand

    # Start displaying logs
    display_logs(log_queue, log_text)

    root.mainloop()

# Run the GUI
create_gui()
