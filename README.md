# Manga to CBZ Converter - Tutorial

This tool converts manga image folders into `.cbz` files. It scans the input directory, converts each manga folder, and saves the `.cbz` files into an output directory.

## How It Works:

1. **Input Directory**: The program detects all subfolders (each containing images of a manga) in the specified input path.

    - Example:
      ```
      D:/PATHWITHMANGAS/
        ├── Manga1/
        ├── Manga2/
        └── Manga3/
      ```

    Each folder (e.g., `Manga1`, `Manga2`, etc.) is converted into a `.cbz` file.

2. **Output Directory**: The `.cbz` files will be saved in the output path you specify.

    - Example:
      ```
      D:/pathwithCBZ/
        ├── Manga1.cbz
        ├── Manga2.cbz
        └── Manga3.cbz
      ```

## Steps:

1. **Prepare Input Directory**:
   - Place your manga folders inside a main folder. The program will scan and convert each subfolder.
   - Example structure:
     ```
     D:/PATHWITHMANGAS/
       ├── OnePiece/
       ├── Naruto/
       └── Bleach/
     ```

2. **Prepare Output Directory**:
   - Create an empty folder where `.cbz` files will be saved.
   - Example:
     ```
     D:/pathwithCBZ/
     ```

3. **Run the Program**:
   - Select the input and output directories when prompted by the program.
   - The program will create `.cbz` files from the manga folders and save them in the output directory.

4. **Automatic Skipping**:
   - If a `.cbz` file already exists in the output directory for a given folder, the program will skip converting that folder.

That's it! Now your `.cbz` files will be ready in the output folder.
