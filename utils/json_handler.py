import json
import os
import asyncio

# This lock will prevent race conditions where multiple functions
# try to read/write to the file at the exact same time.
_lock = asyncio.Lock()
_file_path = "levels.json"

async def load_data():
    """
    Asynchronously loads data from the JSON file.
    If the file doesn't exist, it creates it with an empty object.
    """
    async with _lock:
        # Create the file if it doesn't exist
        if not os.path.exists(_file_path):
            with open(_file_path, 'w') as f:
                json.dump({}, f)
            return {}
        
        # Read the data from the file
        with open(_file_path, 'r', encoding='utf-8') as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                # If the file is corrupted or empty, return an empty dict
                return {}

async def save_data(data):
    """
    Asynchronously saves the provided data to the JSON file.
    """
    async with _lock:
        with open(_file_path, 'w', encoding='utf-8') as f:
            # indent=4 makes the JSON file human-readable
            json.dump(data, f, indent=4)
