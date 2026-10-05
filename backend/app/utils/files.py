import os
import hashlib
import re
import zipfile

def ensure_dir(path: str):
    """Ensures that a directory exists."""
    os.makedirs(path, exist_ok=True)

def safe_filename(name: str) -> str:
    """Converts a string to a safe filename."""
    return re.sub(r'[^a-zA-Z0-9_\-.]', '_', name)

def compute_hash(filepath: str) -> str:
    """Computes the SHA256 hash of a file."""
    sha256_hash = hashlib.sha256()
    with open(filepath, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()

def zip_directory(dir_path: str, output_path: str) -> str:
    """Zips a directory and its contents."""
    with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(dir_path):
            for file in files:
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, dir_path)
                zipf.write(file_path, arcname)
    return output_path
