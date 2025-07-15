#!/usr/bin/env python3
"""
Script to help restart the server safely
"""

import subprocess
import time
import sys
import requests

def check_server_running():
    """Check if server is responding"""
    try:
        response = requests.get("http://localhost:8000/health", timeout=2)
        return response.status_code == 200
    except:
        return False

def find_and_kill_server():
    """Find and kill existing server process"""
    try:
        # Find processes running on port 8000
        result = subprocess.run(
            ["netstat", "-ano", "|", "findstr", ":8000"],
            shell=True,
            capture_output=True,
            text=True
        )
        
        if result.stdout:
            print("🔍 Found processes on port 8000:")
            print(result.stdout)
            
            # Extract PID (Windows netstat format)
            lines = result.stdout.strip().split('\n')
            for line in lines:
                if ':8000' in line and 'LISTENING' in line:
                    parts = line.split()
                    if len(parts) > 4:
                        pid = parts[-1]
                        print(f"📌 Killing process {pid}")
                        subprocess.run(["taskkill", "/F", "/PID", pid], capture_output=True)
        else:
            print("✅ No processes found on port 8000")
            
    except Exception as e:
        print(f"❌ Error finding processes: {e}")

def start_server():
    """Start the server with uvicorn"""
    print("🚀 Starting server...")
    try:
        # Start server in background
        process = subprocess.Popen([
            "python", "-m", "uvicorn", 
            "mcp_server.main:app", 
            "--host", "0.0.0.0", 
            "--port", "8000",
            "--reload"
        ])
        
        # Wait a bit for startup
        time.sleep(3)
        
        if check_server_running():
            print("✅ Server started successfully!")
            return process
        else:
            print("❌ Server failed to start")
            return None
            
    except Exception as e:
        print(f"❌ Error starting server: {e}")
        return None

def main():
    print("🔧 Ardour MCP Server Restart Helper")
    print("=" * 40)
    
    print("Step 1: Checking current server status...")
    if check_server_running():
        print("✅ Server is currently running")
        
        print("\nStep 2: Stopping existing server...")
        find_and_kill_server()
        time.sleep(2)
        
        if check_server_running():
            print("⚠️  Server still running - may need manual intervention")
        else:
            print("✅ Server stopped")
    else:
        print("ℹ️  No server currently running")
    
    print("\nStep 3: Starting new server...")
    process = start_server()
    
    if process:
        print("\n🎯 SUCCESS! Server restarted with new code")
        print("   - All Phase 2 endpoints should now work")
        print("   - OSC format should be fixed")
        print("\n🔍 Test with: python diagnose_server.py")
    else:
        print("\n❌ FAILED to restart server")
        print("   - Try manually: uvicorn mcp_server.main:app --reload")

if __name__ == "__main__":
    main()