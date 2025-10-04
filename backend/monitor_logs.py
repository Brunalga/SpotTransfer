#!/usr/bin/env python3
"""
Script to monitor logs in real-time
"""
import time
import os
import subprocess

def monitor_logs():
    log_file = "spottransfer.log"
    
    if not os.path.exists(log_file):
        print(f"Log file {log_file} not found. Start the server first to create it.")
        return
    
    print(f"Monitoring {log_file} for new log entries...")
    print("Press Ctrl+C to stop monitoring")
    print("-" * 50)
    
    try:
        # Use tail -f to follow the log file
        subprocess.run(["tail", "-f", log_file])
    except KeyboardInterrupt:
        print("\nStopped monitoring logs.")
    except FileNotFoundError:
        print("'tail' command not found. Please install it or use a different method to monitor the log file.")

if __name__ == "__main__":
    monitor_logs()
