#!/usr/bin/env python3
"""
Script to watch the progress of playlist creation in real-time
"""
import time
import os
import re

def watch_progress():
    log_file = "spottransfer.log"
    
    if not os.path.exists(log_file):
        print(f"Log file {log_file} not found.")
        return
    
    print("🔍 Watching playlist creation progress...")
    print("Press Ctrl+C to stop")
    print("-" * 60)
    
    last_position = 0
    
    try:
        while True:
            with open(log_file, 'r') as f:
                f.seek(last_position)
                new_lines = f.readlines()
                last_position = f.tell()
                
                for line in new_lines:
                    line = line.strip()
                    if not line:
                        continue
                    
                    # Look for progress indicators
                    if "Progress:" in line:
                        # Extract progress info
                        match = re.search(r'Progress: (\d+)/(\d+) tracks processed \(([\d.]+)%\)', line)
                        if match:
                            current, total, percentage = match.groups()
                            print(f"📊 Progress: {current}/{total} ({percentage}%)")
                    
                    elif "Found so far:" in line:
                        # Extract found/missed info
                        match = re.search(r'Found so far: (\d+) tracks, Missed: (\d+) tracks', line)
                        if match:
                            found, missed = match.groups()
                            print(f"✅ Found: {found}, ❌ Missed: {missed}")
                    
                    elif "Search completed" in line:
                        print(f"🎉 {line}")
                        return
                    
                    elif "Error" in line or "Exception" in line:
                        print(f"❌ ERROR: {line}")
                    
                    elif "Starting search" in line:
                        print(f"🚀 {line}")
                    
                    elif "Searching for tracks" in line:
                        print(f"🔍 {line}")
            
            time.sleep(2)  # Check every 2 seconds
            
    except KeyboardInterrupt:
        print("\n👋 Stopped watching progress.")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    watch_progress()
