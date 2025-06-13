#!/usr/bin/env bash
# ---------------------------------------------------------------------------
# Sawt end-to-end launcher
# ---------------------------------------------------------------------------
# 1. Builds the Rust voice-to-text engine (Core/input/app)
# 2. Streams the recognized text to the Agent-S runner
# ---------------------------------------------------------------------------
set -euo pipefail

VOICE_ENGINE_MANIFEST="Core/input/app/Cargo.toml"
RUNNER="Core/execution/simple_automation.py"

# Activate virtual environment
if [[ ! -d "venv" ]]; then
    echo "❌ Virtual environment not found. Please run:"
    echo "   python3 -m venv venv"
    echo "   source venv/bin/activate"
    echo "   pip install -r requirements.txt"
    exit 1
fi

source venv/bin/activate

# Compile the Rust programme in release mode (does nothing if already built)
if [[ ! -f Core/input/app/target/release/app ]]; then
  echo "🔧 Building Rust voice engine (release)…"
  cargo build --release --manifest-path "$VOICE_ENGINE_MANIFEST"
fi

# Run the voice engine and pipe its stdout to the Agent-S runner
echo "🚀 Starting Sawt pipeline (voice → simple automation)…"
exec cargo run --quiet --release --manifest-path "$VOICE_ENGINE_MANIFEST" | \
     python "$RUNNER" 