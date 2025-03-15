import os
import time
from datetime import datetime, timedelta

def get_recent_json_files(directory, hours=3):
    """Finds all JSON files created within the last `hours` in the specified directory."""
    json_files = [os.path.join(directory, f) for f in os.listdir(directory) if f.endswith(".json")]
    
    if not json_files:
        return []
    
    # Get current time and the threshold time (3 hours ago)
    current_time = time.time()
    threshold_time = current_time - (hours * 3600)

    # Filter files created within the last `hours`
    recent_files = [f for f in json_files if os.stat(f).st_ctime >= threshold_time]

    return sorted(recent_files, key=lambda f: os.stat(f).st_ctime, reverse=True)  # Sort from newest to oldest