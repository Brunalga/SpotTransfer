#!/usr/bin/env python3
"""
Script to check the current status of playlist creation
"""
import os
import re
from datetime import datetime

def check_status():
    log_file = "spottransfer.log"
    
    if not os.path.exists(log_file):
        print("❌ Log file not found. Server may not be running.")
        return
    
    print("🔍 Checking current playlist creation status...")
    print("-" * 50)
    
    with open(log_file, 'r') as f:
        lines = f.readlines()
    
    # Get the last few lines
    recent_lines = lines[-20:] if len(lines) > 20 else lines
    
    # Look for key indicators
    last_progress = None
    last_error = None
    last_success = None
    total_tracks = None
    
    for line in recent_lines:
        line = line.strip()
        
        # Extract total tracks
        if "Starting search for" in line:
            match = re.search(r'Starting search for (\d+) tracks', line)
            if match:
                total_tracks = int(match.group(1))
        
        # Extract progress
        if "Progress:" in line:
            match = re.search(r'Progress: (\d+)/(\d+) tracks processed \(([\d.]+)%\)', line)
            if match:
                current, total, percentage = match.groups()
                last_progress = {
                    'current': int(current),
                    'total': int(total),
                    'percentage': float(percentage)
                }
        
        # Look for errors
        if "ERROR" in line or "Exception" in line:
            last_error = line
        
        # Look for success
        if "Playlist created successfully" in line:
            last_success = line
    
    # Display status
    if total_tracks:
        print(f"📊 Total tracks to process: {total_tracks}")
    
    if last_progress:
        print(f"📈 Last progress: {last_progress['current']}/{last_progress['total']} ({last_progress['percentage']:.1f}%)")
        
        # Calculate estimated time remaining
        if last_progress['current'] > 0:
            elapsed_per_track = 1.0  # Rough estimate
            remaining_tracks = last_progress['total'] - last_progress['current']
            estimated_time = remaining_tracks * elapsed_per_track
            print(f"⏱️  Estimated time remaining: ~{estimated_time/60:.1f} minutes")
    else:
        print("⏳ No progress data found yet...")
    
    if last_error:
        print(f"❌ Last error: {last_error}")
    
    if last_success:
        print(f"✅ {last_success}")
    
    # Show recent activity
    print("\n📋 Recent activity:")
    for line in recent_lines[-5:]:
        if line.strip():
            print(f"   {line.strip()}")

if __name__ == "__main__":
    check_status()
