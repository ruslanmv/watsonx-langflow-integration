# IBM watsonx.ai Integration with Langflow

This tutorial presents a complete and structured guide to integrating **IBM watsonx.ai** foundation models into the **Langflow** visual programming environment using custom components. You will learn how to install Langflow, configure IBM watsonx.ai, develop chatbot and agent flows, and incorporate vector-based Retrieval Augmented Generation (RAG).

---

## Project Structure Overview

```
langflow-watsonx-integration/
├── .gitignore
├── LICENSE
├── README.md
├── requirements.txt
└── components/
    ├── llm/
    │   └── watsonx.py              # IBM watsonx.ai LLM integration
    └── embeddings/
        └── watsonx_embedding.py    # IBM watsonx.ai Embedding integration
```

This structure allows you to easily extend or embed the components into a Langflow-based application.

---

## Features of the Integration

- Custom components compatible with Langflow's architecture.
- Secure API key handling using `SecretStrInput`.
- Comprehensive parameterization of text generation (temperature, top_p, max_tokens, logprobs, etc.).
- Automatic dynamic retrieval of available watsonx.ai models.
- Embedding generation for use in RAG and vector search pipelines.
- Example agent flow integration with Langflow’s tool-calling framework.

---

## Installation and Environment Setup

### Prerequisites

To install Langflow and use this integration, you will need:

- Python 3.10 to 3.13
- `uv`, `pip`, or `pipx` for package management (uv is recommended)
- A virtual environment for isolation (optional but recommended)
- An IBM watsonx.ai account with a valid API key and project ID

### Step 1: Install Langflow

Using `uv` (recommended):

```bash
uv pip install langflow
```

Using `pip`:

```bash
python -m pip install langflow
```

Using `pipx`:

```bash
pipx install langflow --python python3.10
```

### Step 2: Verify Installation

To start Langflow:

```bash
# With uv
uv run langflow run

# With pip
python -m langflow run
```

Once running, open your browser and navigate to:

```
http://127.0.0.1:7860
```

You should see the Langflow visual interface.

---

## Adding IBM watsonx.ai Integration

### Step 1: Prepare Components

Create directories for Langflow custom components:

```bash
mkdir -p ~/.langflow/components/llm ~/.langflow/components/embeddings
```

Copy the provided files into these locations:

```bash
cp components/llm/watsonx.py ~/.langflow/components/llm/
cp components/embeddings/watsonx_embedding.py ~/.langflow/components/embeddings/
```

### Step 2: Configure IBM watsonx.ai Access

To use IBM watsonx.ai, you will need:

- An IBM Cloud account
- A watsonx.ai project
- A project ID
- An API key

Visit [IBM watsonx.ai](https://dataplatform.cloud.ibm.com/) to create a project and retrieve these values.

Supported endpoint regions include:

- `https://us-south.ml.cloud.ibm.com`
- `https://eu-de.ml.cloud.ibm.com`
- `https://eu-gb.ml.cloud.ibm.com`
- `https://au-syd.ml.cloud.ibm.com`
- `https://jp-tok.ml.cloud.ibm.com`
- `https://ca-tor.ml.cloud.ibm.com`

### Step 3: Test Available Models

Run the following script to list available foundation models in your region:

```bash
python componets/utils/models.py
```

This script queries the watsonx.ai model endpoint for currently supported models and lists them in the terminal.

---

## Creating Your First Langflow Flow with watsonx.ai

### Step-by-Step Guide

1. Open Langflow and click on **New Flow > Blank Flow**.
2. From the sidebar, drag and drop the following components onto the canvas:
    - Chat Input
    - Prompt
    - Chat Output
    - IBM watsonx.ai LLM (visible if your component was correctly installed)
3. Connect the components:
    - Chat Input → Prompt → IBM watsonx.ai → Chat Output
4. Configure the `IBM watsonx.ai` node:
    - **API Key**: paste your watsonx.ai API key
    - **Project ID**: your project identifier
    - **Endpoint URL**: select your regional base URL
    - **Model Name**: choose from dynamically loaded models
    - Optional: Tune generation parameters such as `temperature`, `max_tokens`, etc.
5. Click **Playground** to start an interactive session and test your chatbot.

---

## Embedding and Vector Search (RAG Workflow)

The `watsonx_embedding.py` component supports vector generation for use in RAG pipelines.

### Example Flow

Use this flow to search documents contextually:

```
Chat Input → Prompt → Embedding → Vector Store → Retriever → Prompt → IBM watsonx.ai → Chat Output
```

You may use any vector store Langflow supports (e.g., Astra DB, Chroma, FAISS). Make sure embeddings are indexed before querying.

---

## Building a Simple Agent with Langflow and watsonx.ai

Langflow supports tool-enabled agents. Here’s how to set up a basic agent that can use tools and watsonx.ai for reasoning.

### Create a Simple Agent Flow

1. Click **New Flow > Simple Agent**.
2. Replace the default LLM component with `IBM watsonx.ai`.
3. Add tools like:
    - URL reader (to fetch content)
    - Calculator
4. Connect tools to the `Tool Calling Agent`.
5. Connect:
    - Chat Input → Agent
    - Agent → Chat Output
6. Test it using Playground.

Example query:  
**"Create a tabletop RPG character."**  
You’ll see the agent select tools and use watsonx.ai to return structured answers.

---

## Using the Component in Python Code

For CLI or script testing, use the component standalone:

```python
from components.llm.watsonx import WatsonxComponent

component = WatsonxComponent()
llm = component.build_model()
response = llm("Tell me about the IBM watsonx.ai platform.")
print(response)
```

This allows you to integrate IBM watsonx.ai outside the Langflow UI if needed.

---

## Troubleshooting & Support

- If `langflow run` fails, use:  
  `python -m langflow run`

- If installation hangs on dependency resolution:  
  Use `uv pip install langflow` to bypass `pip`’s resolution lag.

- Migration error?  
  Clear `.cache/langflow/` directory in your home folder.

---

## License

This integration is provided under the terms of the MIT License. See the `LICENSE` file for full details.

---

## Conclusion

This tutorial demonstrated how to:

- Set up Langflow locally
- Integrate IBM watsonx.ai using custom Langflow components
- Build flows including chatbots and agents
- Extend with embedding and vector retrieval

This foundation allows you to prototype and build powerful AI workflows using IBM’s foundation models and Langflow’s user-friendly environment.


