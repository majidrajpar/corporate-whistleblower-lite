"""File tools for reading, writing, and editing files in the project."""
import os
from pathlib import Path

def read_file(file_path: str) -> str:
    """Read a file and return its contents."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        return f"Error reading file: {str(e)}"

def write_file(file_path: str, content: str) -> str:
    """Write content to a file, creating directories if needed."""
    try:
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        return f"Successfully wrote to {file_path}"
    except Exception as e:
        return f"Error writing file: {str(e)}"

def edit_file(file_path: str, old_string: str, new_string: str) -> str:
    """Edit a file by replacing old_string with new_string."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        if old_string not in content:
            return f"Error: old_string not found in {file_path}"
        
        new_content = content.replace(old_string, new_string, 1)
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        
        return f"Successfully edited {file_path}"
    except Exception as e:
        return f"Error editing file: {str(e)}"

def list_files(directory: str, pattern: str = "*") -> str:
    """List files in a directory matching a pattern."""
    try:
        path = Path(directory)
        files = list(path.glob(pattern))
        return "\n".join([str(f.relative_to(path.parent)) for f in files])
    except Exception as e:
        return f"Error listing files: {str(e)}"

def file_exists(file_path: str) -> bool:
    """Check if a file exists."""
    return os.path.isfile(file_path)

def ensure_dir(directory: str) -> str:
    """Ensure a directory exists."""
    try:
        os.makedirs(directory, exist_ok=True)
        return f"Directory ensured: {directory}"
    except Exception as e:
        return f"Error ensuring directory: {str(e)}"
