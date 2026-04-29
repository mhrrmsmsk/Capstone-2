#!/bin/bash
# Quick start script for Streamlit interface
# Usage: ./start_streamlit.sh

cd "$(dirname "$0")"

VENV_PYTHON=".venv/bin/python"
BASE_PYTHON="$(command -v python3.11 || command -v python3.12 || command -v python3)"

echo "🌾 Starting Crop Recommendation Streamlit App..."
echo ""

# Create a local virtual environment if needed or if it was created with an incompatible Python version
if [[ ! -x "$VENV_PYTHON" ]] || ! "$VENV_PYTHON" --version | grep -q "Python 3.11"; then
    echo "📦 Creating local virtual environment (.venv)..."
    rm -rf .venv
    "$BASE_PYTHON" -m venv .venv
fi

# Install dependencies inside the virtual environment
"$VENV_PYTHON" -m pip install --upgrade pip
"$VENV_PYTHON" -m pip install -r requirements.txt

# Start the app using the virtual environment
"$VENV_PYTHON" -m streamlit run streamlit_app.py
