#!/bin/bash

# Script to create and set up a Python virtual environment.

# Check if the virtual environment (.venv) already exists in the root directory.
if [ -d ".venv" ]; then
    echo ".venv already exists. Loading the virtual environment..."
else
    echo "Creating virtual environment (.venv)..."
    python3 -m venv .venv
    if [ $? -ne 0 ]; then
        echo "❌ Error: Failed to create virtual environment. Please ensure Python 3 is properly installed."
        exit 1
    fi
fi

# Activate the virtual environment.
echo "✅ Activating virtual environment..."
source .venv/bin/activate

# Upgrade pip to the latest version.
echo "⬆️ Upgrading pip..."
pip install --upgrade pip

# Install dependencies from requirements.txt if it exists.
if [ -f "requirements.txt" ]; then
    echo "📦 Installing dependencies from requirements.txt..."
    pip install -r requirements.txt
else
    echo "📄 requirements.txt not found. Skipping dependency installation."
fi

echo "🎉 Environment setup is complete."