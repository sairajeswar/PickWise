import os
import zipfile

SOURCE_DIR = r"C:\Users\hp\.gemini\antigravity\scratch\pickwise"
DEST_ZIP = r"C:\Users\hp\Desktop\PickWise.zip"

EXCLUDE_DIRS = {
    "node_modules",
    "__pycache__",
    ".pytest_cache",
    ".git",
    "dist"
}

EXCLUDE_EXTS = {
    ".pyc"
}

def create_project_zip():
    print(f"Creating zip archive at: {DEST_ZIP}")
    os.makedirs(os.path.dirname(DEST_ZIP), exist_ok=True)
    
    with zipfile.ZipFile(DEST_ZIP, "w", zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(SOURCE_DIR):
            # Prune excluded directories
            dirs[:] = [d for d in dirs if d not in EXCLUDE_DIRS]
            
            for file in files:
                if any(file.endswith(ext) for ext in EXCLUDE_EXTS):
                    continue
                file_path = os.path.join(root, file)
                rel_path = os.path.relpath(file_path, SOURCE_DIR)
                zipf.write(file_path, rel_path)
                
    zip_size_mb = os.path.getsize(DEST_ZIP) / (1024 * 1024)
    print(f"Zip created successfully! Size: {zip_size_mb:.2f} MB")

if __name__ == "__main__":
    create_project_zip()
