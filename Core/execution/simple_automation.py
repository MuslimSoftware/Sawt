"""Simple automation runner for local LLaMA models.

This is a simplified alternative to Agent-S2 that works better with local models
by avoiding complex JSON formatting requirements and using direct action execution.
"""

import io
import os
import platform
import sys
import re
import json
from pathlib import Path

import pyautogui
import requests
import subprocess
import time

# --- LLM Configuration ---
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434/v1")
LLAMA_MODEL = os.getenv("LLAMA_MODEL", "llama3.1:8b")

# --- System Prompt ---
SYSTEM_PROMPT = f"""You are a computer automation assistant running on {platform.system()}. 
Your job is to help users control their computer by generating Python code using pyautogui.

IMPORTANT RULES:
1. Only generate Python code using pyautogui functions
2. Use simple, direct actions - no complex planning
3. Always wrap your code in ```python and ``` tags
4. For macOS, use common keyboard shortcuts (Cmd+Space for Spotlight, etc.)
5. Be conservative - prefer keyboard shortcuts over clicking coordinates
6. Add appropriate sleep delays between actions (0.5-1.0 seconds)
7. Avoid hardcoded click coordinates when possible - use keyboard navigation instead

Available pyautogui functions:
- pyautogui.hotkey('cmd', 'space') - press key combination (preferred)
- pyautogui.press('key') - press a key
- pyautogui.write('text') - type text
- pyautogui.sleep(seconds) - wait between actions
- pyautogui.click(x, y) - click at coordinates (use sparingly)
- pyautogui.scroll(clicks) - scroll up/down

macOS-specific shortcuts:
- Cmd+Space: Open Spotlight
- Cmd+T: New tab in browser
- Cmd+L: Focus address bar in browser
- Cmd+Tab: Switch between apps
- Cmd+W: Close window/tab

Example for "open calculator":
```python
# Open Spotlight search
pyautogui.hotkey('cmd', 'space')
pyautogui.sleep(0.5)
# Type calculator
pyautogui.write('calculator')
pyautogui.sleep(0.5)
# Press Enter
pyautogui.press('enter')
```

Example for "search Google for cats":
```python
# Open Spotlight to launch browser
pyautogui.hotkey('cmd', 'space')
pyautogui.sleep(0.5)
pyautogui.write('chrome')
pyautogui.sleep(0.5)
pyautogui.press('enter')
pyautogui.sleep(2)  # Wait for Chrome to open

# Focus address bar and go to Google
pyautogui.hotkey('cmd', 'l')
pyautogui.sleep(0.5)
pyautogui.write('google.com')
pyautogui.press('enter')
pyautogui.sleep(2)  # Wait for Google to load

# Type search query (Google search box gets focus automatically)
pyautogui.write('cats')
pyautogui.press('enter')
```

Now help the user with their request."""

def call_llama(prompt: str, system_prompt: str = SYSTEM_PROMPT) -> str:
    """Call local LLaMA model via Ollama API."""
    try:
        response = requests.post(
            f"{OLLAMA_BASE_URL}/chat/completions",
            json={
                "model": LLAMA_MODEL,
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt}
                ],
                "max_tokens": 500,
                "temperature": 0.1
            },
            timeout=30
        )
        response.raise_for_status()
        
        result = response.json()
        return result["choices"][0]["message"]["content"]
    
    except Exception as e:
        return f"Error calling LLaMA: {e}"

def extract_python_code(text: str) -> str:
    """Extract Python code from markdown code blocks."""
    # Look for ```python ... ``` blocks
    pattern = r'```python\s*(.*?)\s*```'
    matches = re.findall(pattern, text, re.DOTALL)
    
    if matches:
        return matches[0].strip()
    
    # Fallback: look for any ``` blocks
    pattern = r'```\s*(.*?)\s*```'
    matches = re.findall(pattern, text, re.DOTALL)
    
    if matches:
        return matches[0].strip()
    
    return ""

def check_accessibility_permissions():
    """Check if the script has accessibility permissions on macOS."""
    try:
        # Try to get screen size - this requires accessibility permissions
        pyautogui.size()
        return True
    except Exception:
        return False

def request_accessibility_permissions():
    """Guide user to grant accessibility permissions."""
    print("🔒 ACCESSIBILITY PERMISSIONS REQUIRED")
    print("📋 To control your Mac, this app needs accessibility permissions:")
    print("   1. Go to System Preferences → Security & Privacy → Privacy")
    print("   2. Click 'Accessibility' in the left sidebar")
    print("   3. Click the lock icon and enter your password")
    print("   4. Add 'Terminal' or 'Python' to the list")
    print("   5. Make sure it's checked ✅")
    print("   6. Restart this script")
    print("🔗 Or run: open 'x-apple.systempreferences:com.apple.preference.security?Privacy_Accessibility'")

def execute_instruction(instruction: str):
    """Execute a natural language instruction using local LLaMA."""
    if not instruction.strip():
        return
    
    print(f"\n{'='*60}")
    print(f"📥 RECEIVED INSTRUCTION: '{instruction}'")
    print(f"{'='*60}")
    
    # Check accessibility permissions first
    if not check_accessibility_permissions():
        request_accessibility_permissions()
        return
    
    # Get response from LLaMA
    print("🧠 Calling LLaMA model...")
    response = call_llama(instruction)
    print(f"💭 LLaMA response:\n{response}")
    print(f"{'-'*40}")
    
    # Extract Python code
    code = extract_python_code(response)
    
    if not code:
        print("⚠️  No executable code found in response")
        print("🔍 Looking for code blocks in response...")
        return
    
    print(f"🐍 EXTRACTED CODE:")
    print(f"{code}")
    print(f"{'-'*40}")
    print("⚡ EXECUTING AUTOMATION...")
    
    # Give user a moment to see what's about to happen
    print("⏱️  Starting in 2 seconds...")
    time.sleep(2)
    
    try:
        # Add pyautogui import and safety settings
        safe_code = f"""
import pyautogui
import time
import subprocess

# Safety settings
pyautogui.FAILSAFE = True
pyautogui.PAUSE = 0.2  # Slightly slower for reliability

# Switch focus away from terminal to desktop
# First, minimize or hide terminal window
pyautogui.hotkey('cmd', 'm')  # Minimize current window (terminal)
time.sleep(0.5)

# Click on desktop to ensure we're not in any application
pyautogui.click(500, 300)  # Click somewhere neutral on desktop
time.sleep(0.5)

{code}
"""
        
        exec(safe_code, {"__builtins__": __builtins__, "subprocess": subprocess})
        print("✅ AUTOMATION COMPLETED SUCCESSFULLY")
        
    except Exception as e:
        print(f"❌ AUTOMATION ERROR: {e}")
        print(f"🔧 Code that failed:\n{code}")
        if "accessibility" in str(e).lower():
            request_accessibility_permissions()
    
    print(f"{'='*60}\n")

def _interactive_loop():
    """Interactive shell for testing."""
    print("🤖 Simple Automation Shell - type instructions, or 'exit' to quit.")
    while True:
        try:
            line = input("Instruction> ")
        except EOFError:
            break
        if line.strip().lower() in {"exit", "quit"}:
            break
        execute_instruction(line)

def _stdin_loop():
    """Read newline-separated instructions from STDIN until EOF."""
    print("🤖 Simple Automation Runner Started")
    print("📡 Waiting for voice commands from Rust engine...")
    print("🎯 Ready to execute automation tasks!")
    print(f"🔗 Connected to LLaMA model: {LLAMA_MODEL}")
    print(f"🌐 Ollama endpoint: {OLLAMA_BASE_URL}")
    print("="*60)
    
    for line in sys.stdin:
        execute_instruction(line.rstrip("\n"))

if __name__ == "__main__":
    if not sys.stdin.isatty() and len(sys.argv) == 1:
        # Piped mode: voice engine's output is streaming in
        _stdin_loop()
    elif len(sys.argv) > 1:
        execute_instruction(" ".join(sys.argv[1:]))
    else:
        _interactive_loop() 