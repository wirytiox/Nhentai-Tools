import os
import xml.etree.ElementTree as ET
import shutil
import re
import tkinter as tk
from tkinter import filedialog, messagebox
import threading
import queue
import zipfile

# Function to extract author and clean title from folder name
def extract_author_and_clean_title(folder_name):
    match = re.match(r'^[\[\(](.*?)[\]\)] ?(.*)', folder_name)
    if match:
        author = match.group(1).strip()  # Extract author or group
        title = match.group(2).strip()   # Extract the rest (title)
        return author, title
    return None, folder_name  # No match found, return folder name as title

# Function to process manga folders, generate XML, and create CBZ files
def process_manga(input_folder, output_folder, log_queue):
    if not os.path.exists(input_folder):
        log_queue.put("Input folder does not exist.\n")
        return

    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    image_extensions = ('.png', '.jpg', '.jpeg', '.webp', '.gif')
    file_name_variations = ['1', '01', '001', '0001']

    directories = [d for d in os.listdir(input_folder) if os.path.isdir(os.path.join(input_folder, d))]

    log_queue.put(f"Processing {len(directories)} directories...\n")

    for directory in directories:
        new_dir_path = os.path.join(output_folder, directory)

        # Create output directory if it doesn't exist
        if not os.path.exists(new_dir_path):
            os.mkdir(new_dir_path)
            log_queue.put(f"Created directory: {new_dir_path}\n")

        # Extract author and title from folder name
        author, cleaned_title = extract_author_and_clean_title(directory)

        # Generate ComicInfo.xml
        comic_info = ET.Element("ComicInfo")
        title_element = ET.SubElement(comic_info, "Title")
        title_element.text = cleaned_title

        if author:
            author_element = ET.SubElement(comic_info, "Author")
            author_element.text = author
            log_queue.put(f"Extracted author: {author}\n")

        # Save ComicInfo.xml (OUTSIDE CBZ)
        comic_info_path = os.path.join(new_dir_path, "ComicInfo.xml")
        tree = ET.ElementTree(comic_info)
        with open(comic_info_path, "wb") as file:
            tree.write(file, encoding="utf-8", xml_declaration=True)
            log_queue.put(f"Written ComicInfo.xml for {cleaned_title} outside CBZ\n")

        # Search for the image file named 1, 01, 001, 0001 with any valid extension
        source_dir = os.path.join(input_folder, directory)
        found = False
        image_files = []

        for filename_base in file_name_variations:
            for ext in image_extensions:
                image_file = os.path.join(source_dir, f"{filename_base}{ext}")
                if os.path.exists(image_file):
                    new_file_name = f"cover{ext}"
                    new_file_path = os.path.join(new_dir_path, new_file_name)
                    shutil.copy(image_file, new_file_path)
                    log_queue.put(f"Copied and renamed {image_file} to {new_file_path} (outside CBZ)\n")
                    found = True
                    break
            if found:
                break

        # Collect all image files for CBZ creation (excluding ComicInfo.xml and cover)
        image_files = [f for f in os.listdir(source_dir) if f.lower().endswith(image_extensions)]
        image_files.sort()  # Sort image files to maintain correct order in CBZ

        if image_files:
            # Create the CBZ file (inside the new directory)
            cbz_filename = os.path.join(new_dir_path, f"{cleaned_title}.cbz")
            log_queue.put(f"Creating CBZ for {cleaned_title}...\n")
            try:
                with zipfile.ZipFile(cbz_filename, 'w') as cbz:
                    # Add all other images (excluding ComicInfo.xml and cover)
                    for image_file in image_files:
                        image_path = os.path.join(source_dir, image_file)
                        cbz.write(image_path, arcname=image_file)
                    log_queue.put(f"CBZ file created: {cbz_filename}\n")

            except Exception as e:
                log_queue.put(f"Error creating CBZ file: {e}\n")
        else:
            log_queue.put(f"No image files found in {directory}\n")

    log_queue.put("Processing completed.\n")

# Function to select a folder
def select_folder(var):
    folder_selected = filedialog.askdirectory()
    if folder_selected:
        var.set(folder_selected)

# Function to start the processing in a separate thread
def start_processing_thread(input_var, output_var, log_queue):
    input_folder = input_var.get()
    output_folder = output_var.get()

    if not input_folder or not output_folder:
        messagebox.showerror("Error", "Please select both input and output directories.")
        return

    log_queue.put("Starting processing...\n")
    threading.Thread(target=process_manga, args=(input_folder, output_folder, log_queue)).start()

# Function to display logs in the text widget
def display_logs(log_queue, log_text):
    while not log_queue.empty():
        log_message = log_queue.get_nowait()
        log_text.insert(tk.END, log_message)
        log_text.see(tk.END)  # Auto-scroll to the bottom

    # Call this function again after 100 ms to check for new logs
    log_text.after(100, display_logs, log_queue, log_text)

# Function to create the GUI
def create_gui():
    root = tk.Tk()
    root.title("Manga Processor")
    root.geometry("700x400")  # Set the window size

    # Variables to store folder paths
    input_var = tk.StringVar()
    output_var = tk.StringVar()

    # Queue for log messages
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
    tk.Button(root, text="Start Processing", command=lambda: start_processing_thread(input_var, output_var, log_queue)).grid(row=2, column=0, columnspan=3, padx=10, pady=10)

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
