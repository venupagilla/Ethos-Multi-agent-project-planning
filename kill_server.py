import os
import subprocess
import sys

def kill_port_8000():
    print("Searching for processes on port 8000...")
    try:
        output = subprocess.check_output('netstat -ano | findstr :8000', shell=True).decode()
        pids = set()
        for line in output.strip().split('\n'):
            parts = line.split()
            if len(parts) > 4:
                pid = parts[-1]
                pids.add(pid)
        
        if not pids:
            print("No processes found on port 8000.")
            return

        print(f"Found PIDs: {pids}")
        for pid in pids:
            try:
                print(f"Killing process {pid}...")
                subprocess.run(f"taskkill /F /PID {pid}", shell=True)
            except Exception as e:
                print(f"Failed to kill {pid}: {e}")
                
    except subprocess.CalledProcessError:
        print("No processes found on port 8000.")

if __name__ == "__main__":
    kill_port_8000()
