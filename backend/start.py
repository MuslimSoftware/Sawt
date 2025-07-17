#!/usr/bin/env python3

"""
Sawt Voice Assistant Startup Script

This script provides an easy way to start the voice assistant server
with proper environment setup and error handling.
"""

import os
import sys
import subprocess
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

def check_environment():
    """Check if required environment variables are set"""
    print("🔍 Checking environment variables...")
    
    required_vars = ["AI_MODEL", "AI_API_KEY"]
    missing_vars = []
    
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        print(f"❌ Missing required environment variables: {', '.join(missing_vars)}")
        print("\nPlease set them before running the server:")
        for var in missing_vars:
            print(f"  export {var}='your-value'")
        return False
        
    print("✅ Environment variables check passed")
    return True

def check_rust_build():
    """Check if Rust components are built (never runs the Rust binary, only checks/builds it)"""
    print("🔍 Checking Rust build...")
    try:
        # Check if cargo is available
        result = subprocess.run(["cargo", "--version"], capture_output=True, text=True, timeout=10)
        if result.returncode != 0:
            print("❌ Cargo not found. Please install Rust toolchain.")
            return False
        # Only check/build, never run the Rust binary (prevents port conflicts)
        result = subprocess.run(
            ["cargo", "check", "--manifest-path", "hardware/app/Cargo.toml"],
            capture_output=True,
            text=True,
            timeout=30
        )
        if result.returncode != 0:
            print("❌ Rust build check failed. Attempting to build...")
            result = subprocess.run(
                ["cargo", "build", "--manifest-path", "hardware/app/Cargo.toml"],
                capture_output=True,
                text=True,
                timeout=60
            )
            if result.returncode != 0:
                print("❌ Rust build failed:")
                print(result.stderr)
                return False
        print("✅ Rust build check passed")
        return True
    except FileNotFoundError:
        print("❌ Cargo not found. Please install Rust toolchain.")
        return False
    except subprocess.TimeoutExpired:
        print("❌ Rust build check timed out")
        return False

def check_port_availability():
    """Check if port 8765 is available and kill any processes using it"""
    print("🔍 Checking port availability...")
    try:
        result = subprocess.run(["lsof", ":8765"], capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            print("❌ Port 8765 is already in use by another process")
            print("Current processes using port 8765")
            print(result.stdout)
            print("Killing existing processes...")
            
            # Kill processes using port 8765
            kill_result = subprocess.run(["lsof", "-ti", ":8765"], capture_output=True, text=True)
            if kill_result.stdout.strip():
                pids = kill_result.stdout.strip().split('\n')
                for pid in pids:
                    if pid.strip():
                        print(f"Killing process {pid}")
                        subprocess.run(["kill", "-9", pid], capture_output=True)
                print("✅ Killed existing processes")
            return True
        else:
            print("✅ Port 8765 is available")
            return True
    except subprocess.TimeoutExpired:
        print("⚠️  Port check timed out, proceeding anyway")
        return True
    except Exception as e:
        print(f"⚠️  Could not check port availability: {e}")
        return True

def main():
    """Main startup function"""
    print("🚀 Sawt Voice Assistant Startup")
    print("=" * 40)
        
    if not check_environment():
        sys.exit(1)

    if not check_rust_build():
        sys.exit(1)
        
    if not check_port_availability():
        sys.exit(1)

    print("\n✅ All checks passed! Starting server...")
    print("=" * 40)
    
    try:
        subprocess.run([sys.executable, "server.py"])
    except KeyboardInterrupt:
        print("\n👋 Server stopped by user")
    except Exception as e:
        print(f"❌ Server error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 