#!/bin/bash

# Exit immediately if a command exits with a non-zero status.
set -e

# --- Configuration ---
# Name of the Python virtual environment directory
ENV_NAME=".venv"
# Relative path to the source component files (assuming script is run from project root)
COMPONENT_SRC_DIR="./components"
# Langflow's directory for custom components in the user's home
LANGFLOW_COMPONENT_DIR="$HOME/.langflow/components"
# --- End Configuration ---

echo "🚀 Starting Langflow Setup & Launch Script for IBM watsonx.ai Integration..."
echo "========================================================================"

# Step 1: Activate the virtual environment
echo "🔄 [Step 1/6] Activating virtual environment '$ENV_NAME'..."
if [ ! -d "$ENV_NAME" ]; then
    echo "❌ Error: Virtual environment directory '$ENV_NAME' not found in the current directory."
    echo "   Please create it first (e.g., 'python3 -m venv $ENV_NAME') and install base requirements if needed."
    exit 1
fi
source "$ENV_NAME/bin/activate"
if [ $? -ne 0 ]; then
    echo "❌ Error: Failed to activate virtual environment '$ENV_NAME'."
    exit 1
fi
echo "✅ Virtual environment activated."

# Step 2: Check Python version
echo "🐍 [Step 2/6] Checking Python version inside the virtual environment..."
# Execute python --version and check its exit status
PYTHON_VERSION_OUTPUT=$(python --version 2>&1) # Capture stdout and stderr
EXIT_STATUS=$?

if [ $EXIT_STATUS -ne 0 ]; then
    echo "❌ Error: Failed to execute 'python --version'."
    echo "   Make sure Python is correctly installed and accessible in the '$ENV_NAME' environment."
    # deactivate # Optional: Deactivate on failure
    exit 1
else
    # Print the captured version info
    echo "   $PYTHON_VERSION_OUTPUT"
    echo "✅ Python version checked successfully. Assuming required packages are installed."
fi
# Step 3: Create Langflow custom component directories
echo "📁 [Step 3/6] Ensuring Langflow custom component directories exist..."
mkdir -p "$LANGFLOW_COMPONENT_DIR/llm" "$LANGFLOW_COMPONENT_DIR/embeddings"
if [ $? -ne 0 ]; then
    echo "❌ Error: Failed to create Langflow component directories in $LANGFLOW_COMPONENT_DIR."
    # deactivate
    exit 1
fi
echo "✅ Component directories ensured at $LANGFLOW_COMPONENT_DIR."

# Step 4: Copy custom watsonx.ai component files
echo "📄 [Step 4/6] Copying custom component files..."

LLM_SRC="$COMPONENT_SRC_DIR/llm/watsonx.py"
EMBED_SRC="$COMPONENT_SRC_DIR/embeddings/watsonx_embeddings.py"
LLM_DEST="$LANGFLOW_COMPONENT_DIR/llm/watsonx.py"
EMBED_DEST="$LANGFLOW_COMPONENT_DIR/embeddings/watsonx_embeddings.py"

# Check if source directory exists
if [ ! -d "$COMPONENT_SRC_DIR/llm" ] || [ ! -d "$COMPONENT_SRC_DIR/embeddings" ]; then
    echo "❌ Error: Source component directory '$COMPONENT_SRC_DIR/llm' or '$COMPONENT_SRC_DIR/embeddings' not found."
    echo "   Make sure you are running this script from the root of the 'langflow-watsonx-integration' project."
    # deactivate
    exit 1
fi

# Copy LLM component
if [ ! -f "$LLM_SRC" ]; then
    echo "❌ Error: LLM component source file not found: $LLM_SRC"
    # deactivate
    exit 1
fi
cp "$LLM_SRC" "$LLM_DEST"
echo "   -> Copied LLM component to $LLM_DEST"

# Copy Embeddings component
if [ ! -f "$EMBED_SRC" ]; then
    echo "❌ Error: Embedding component source file not found: $EMBED_SRC"
    # deactivate
    exit 1
fi
cp "$EMBED_SRC" "$EMBED_DEST"
echo "   -> Copied Embedding component to $EMBED_DEST"

echo "✅ Custom component files copied."

# Step 5: Reminder for IBM watsonx.ai Credentials
echo "🔑 [Step 5/6] Reminder: Prepare your IBM Credentials!"
echo "   You will need:"
echo "     - IBM Cloud API Key"
echo "     - watsonx.ai Project ID"
echo "     - watsonx.ai Regional Endpoint URL (e.g., https://us-south.ml.cloud.ibm.com)"
echo "   These are required to configure the 'IBM watsonx.ai' components inside Langflow."
echo "   Visit https://dataplatform.cloud.ibm.com/ if needed."

# Step 6: Launch Langflow
echo "🚀 [Step 6/6] Launching Langflow..."
echo "========================================================================"
echo "   Access Langflow in your browser (typically http://127.0.0.1:7860)."
echo "   The custom IBM watsonx.ai components should be available in the sidebar."
echo "   Press Ctrl+C in this terminal to stop Langflow."
echo "========================================================================"

# Run Langflow - this command will occupy the terminal until stopped
langflow run

# This part executes only after langflow run is stopped (e.g., by Ctrl+C)
echo ""
echo "========================================================================"
echo "✅ Langflow process stopped."
# Optional: Deactivate environment upon script completion/stopping Langflow
# echo "🔄 Deactivating virtual environment '$ENV_NAME'..."
# deactivate
echo "🎉 Script finished."
echo "========================================================================"

exit 0