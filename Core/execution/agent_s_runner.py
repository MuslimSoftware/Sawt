"""Bare-bones Agent S2 runner wired to a local LLaMA model.

This script is the bridge between Sawt's voice-to-text pipeline (Core/input) and
Agent S2, an open-source computer-use agent.  It expects to receive plaintext
commands (for now via STDIN or CLI args) and executes the actions returned by
Agent S2 on macOS using `pyautogui`.

Prerequisites
-------------
1. Install the package that hosts Agent S2:

   pip install gui-agents  # provides gui_agents.s2.AgentS2, etc.

2. Run a local OpenAI-compatible server for a LLaMA model – e.g. using
   Ollama:

       brew install ollama
       ollama run llama3  # the model name you want

   This exposes an OpenAI-style chat endpoint on http://localhost:11434/v1.

3. Ensure the environment variable below points to that endpoint; otherwise the
   defaults should work:

       export OLLAMA_BASE_URL=http://localhost:11434/v1
       export LLAMA_MODEL=llama3

Usage
-----
Interactive shell:

    python Core/execution/agent_s_runner.py

CLI one-shot:

    python Core/execution/agent_s_runner.py "Open a new tab in Chrome and search for DSPy"

Integrating with the Rust voice engine
--------------------------------------
The simplest glue code is to pipe the Rust program's STDOUT into this script's
STDIN, e.g.:

    cargo run --release --manifest-path Core/input/app/Cargo.toml | \
        python Core/execution/agent_s_runner.py

In the future we can replace this with a Unix socket, message queue, or any
other IPC mechanism.
"""

import io
import os
import platform
import sys
from pathlib import Path

# Set dummy OpenAI API key before any gui_agents imports
os.environ.setdefault("OPENAI_API_KEY", "dummy-key-for-local-llm")
# Set dummy Perplexica URL to avoid search engine errors
os.environ.setdefault("PERPLEXICA_URL", "http://localhost:3001/api/search")

import pyautogui

try:
    # Correct import path for AgentS2 in gui-agents 0.2.x
    from gui_agents.s2.agents.agent_s import AgentS2
except ImportError as exc:
    raise ImportError(
        "gui-agents 0.2.x not found or incompatible. Make sure it's installed with `pip install gui-agents>=0.2.4`."
    ) from exc

# --- LLM engine configuration ---------------------------------------------

_engine_params = {
    "engine_type": "openai",  # Agent S2 expects this literal key
    "base_url": os.getenv("OLLAMA_BASE_URL", "http://localhost:11434/v1"),
    "api_key": os.getenv("OLLAMA_API_KEY", "ollama"),  # any non-empty string
    "model": os.getenv("LLAMA_MODEL", "llama3.1:8b"),
}

# --- Grounding (use OSWorldACI which is platform-agnostic) -----------------
from gui_agents.s2.agents.grounding import OSWorldACI

grounding_agent = OSWorldACI(
    platform=platform.system().lower(),
    engine_params_for_generation=_engine_params,
    engine_params_for_grounding=_engine_params,
)

# --- Instantiate Agent S2 --------------------------------------------------

agent = AgentS2(
    _engine_params,
    grounding_agent,
    platform=platform.system().lower(),  # e.g. "darwin", "windows", "linux"
    action_space="pyautogui",
    observation_type="screenshot",  # simplest mode for now
    search_engine=None,  # Disable web search for now
)


def _capture_observation() -> dict:
    """Capture the observation expected by Agent S2 (screenshot only)."""
    screenshot = pyautogui.screenshot()
    buf = io.BytesIO()
    screenshot.save(buf, format="PNG")
    return {"screenshot": buf.getvalue()}


def execute_instruction(instruction: str):
    """Run a single natural-language instruction through Agent S2."""
    if not instruction.strip():
        return

    obs = _capture_observation()
    info, actions = agent.predict(instruction=instruction, observation=obs)

    if not actions:
        print("⚠️  Agent returned no actions.")
        return

    print(f"ℹ️  Agent info: {info}")
    print(f"➡️  Executing {len(actions)} action(s) …")

    # Each element in `actions` is Python code (usually pyautogui calls).
    for idx, act in enumerate(actions, 1):
        print(f"   [Action {idx}] {act}")
        try:
            exec(act, globals(), locals())
        except Exception as exc:
            print(f"   ❌ Error executing action {idx}: {exc}")


# ---------------------------------------------------------------------------
# CLI / pipe mode
# ---------------------------------------------------------------------------

def _interactive_loop():
    print("💻 Agent S2 shell — type instructions, or Ctrl-D / 'exit' to quit.")
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