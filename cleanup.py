import os
import shutil

# ---------------- CONFIG ----------------
# Path to the project folder (change if needed)
PROJECT_FOLDER = os.path.dirname(os.path.abspath(__file__))

# File extensions to delete
FILE_EXTENSIONS = ['.pyc', '.pyo', '.db', '.sqlite']

# Folders to delete completely (optional)
FOLDERS_TO_DELETE = ['__pycache__']

# ---------------- CLEANUP ----------------
def clean_files(folder):
    deleted_files = []
    for root, dirs, files in os.walk(folder):
        # Delete files with specific extensions
        for file in files:
            if any(file.endswith(ext) for ext in FILE_EXTENSIONS):
                file_path = os.path.join(root, file)
                os.remove(file_path)
                deleted_files.append(file_path)
        # Delete specific folders
        for d in dirs:
            if d in FOLDERS_TO_DELETE:
                folder_path = os.path.join(root, d)
                shutil.rmtree(folder_path)
                deleted_files.append(folder_path)
    return deleted_files

if __name__ == "__main__":
    deleted = clean_files(PROJECT_FOLDER)
    if deleted:
        print("Deleted the following files/folders:")
        for f in deleted:
            print(f" - {f}")
    else:
        print("Nothing to delete!")
