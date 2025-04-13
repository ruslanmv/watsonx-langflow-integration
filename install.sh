#!/bin/bash

# Install Langflow on WSL Ubuntu 22.04 using Python 3.11 and pyproject.toml

echo "Starting Langflow installation on Ubuntu 22.04 with Python 3.11..."

# Step 1: Update package lists
echo "Step 1: Updating package lists..."
sudo apt update

# Step 2: Install necessary dependencies
echo "Step 2: Installing necessary dependencies..."
sudo apt install -y software-properties-common curl

# Step 3: Add deadsnakes PPA for Python 3.11
echo "Step 3: Adding deadsnakes PPA for Python 3.11..."
sudo add-apt-repository ppa:deadsnakes/ppa -y
sudo apt update

# Step 4: Install Python 3.11
echo "Step 4: Installing Python 3.11..."
sudo apt install -y python3.11 python3.11-venv python3.11-dev

# Step 5: Check Python 3.11 installation
echo "Step 5: Checking Python 3.11 installation..."
python3.11 --version

# Step 6: Set Python 3.11 as the default python3
echo "Step 6: Setting Python 3.11 as the default python3..."
sudo update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.11 1
sudo update-alternatives --config python3

# Verify the default python version
echo "Current default Python version:"
python3 --version

# Step 7: Install pip for Python 3.11
echo "Step 7: Installing pip for Python 3.11..."
curl -sS https://bootstrap.pypa.io/get-pip.py | sudo python3.11 -

# Step 8: Upgrade pip
echo "Step 8: Upgrading pip..."
python3 -m pip install --upgrade pip

# Step 9: Install uv (optional, only if using uv)
echo "Step 9: Installing uv..."
python3 -m pip install uv

# Step 10: Create a virtual environment named .venv
ENV_NAME=".venv"
echo "Step 10: Creating a virtual environment named $ENV_NAME..."
python3.11 -m venv "$ENV_NAME"
if [ $? -ne 0 ]; then
    echo "❌ Error: Failed to create virtual environment '$ENV_NAME'."
    exit 1
fi

# Step 11: Activate the virtual environment
echo "Step 11: Activating $ENV_NAME..."
source "$ENV_NAME/bin/activate"
if [ $? -ne 0 ]; then
    echo "❌ Error: Failed to activate virtual environment '$ENV_NAME'."
    exit 1
fi
echo "✅ Activated $ENV_NAME"

# Step 12: Check Python version inside the virtual environment
echo "Step 12: Checking Python version inside the virtual environment..."
python --version

# Step 13: Upgrade pip inside the virtual environment
echo "Step 13: Upgrading pip inside the virtual environment..."
pip install --upgrade pip

# Step 14: Checking for pyproject.toml in the current directory
echo "Step 14: Checking for pyproject.toml..."
if [ -f "./pyproject.toml" ]; then
    echo "✅ pyproject.toml found in the current directory."
else
    echo "⚠️ pyproject.toml not found. Exiting."
    exit 1
fi

# Step 15: Installing dependencies
echo "Step 15: Installing dependencies..."
# uv fails on monorepos; fallback to poetry if needed
if command -v uv &> /dev/null; then
    uv pip install -r <(uv pip compile pyproject.toml)
else
    pip install -r requirements.txt || pip install .
fi

# Step 16: Verify Langflow installation
echo "Step 16: Verifying Langflow installation..."
python -c "import langflow" 2>/dev/null
if [ $? -eq 0 ]; then
    echo "✅ Langflow installed successfully!"
else
    echo "⚠️ Langflow installation might have issues."
fi

# Final Messages
echo "Installation complete."
echo "To run Langflow, activate the environment with: source $ENV_NAME/bin/activate"
echo "Then run: langflow run"
