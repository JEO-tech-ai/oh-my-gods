#!/usr/bin/env bash
# deepagents setup script
# Validates environment and installs the deepagents SDK

set -euo pipefail

echo "=== deepagents Setup ==="
echo ""

# --- Python version check ---
if ! command -v python3 &>/dev/null; then
    echo "ERROR: python3 not found. Install Python 3.11+ first."
    exit 1
fi

python_version=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
major=$(echo "$python_version" | cut -d. -f1)
minor=$(echo "$python_version" | cut -d. -f2)

if [ "$major" -lt 3 ] || ([ "$major" -eq 3 ] && [ "$minor" -lt 11 ]); then
    echo "ERROR: deepagents requires Python >= 3.11 (found $python_version)"
    echo "Upgrade Python: https://python.org/downloads"
    exit 1
fi

echo "✅ Python $python_version — OK"

# --- Install deepagents ---
if command -v uv &>/dev/null; then
    echo "Installing deepagents via uv..."
    uv add deepagents
elif command -v pip &>/dev/null; then
    echo "Installing deepagents via pip..."
    pip install deepagents
else
    echo "ERROR: Neither uv nor pip found."
    echo "Install uv (recommended): curl -LsSf https://astral.sh/uv/install.sh | sh"
    exit 1
fi

echo "✅ deepagents installed"

# --- Optional: MCP adapters ---
if [ "${INSTALL_MCP:-0}" = "1" ]; then
    echo "Installing MCP adapters..."
    if command -v uv &>/dev/null; then
        uv add langchain-mcp-adapters
    else
        pip install langchain-mcp-adapters
    fi
    echo "✅ langchain-mcp-adapters installed"
fi

# --- Optional: provider packages ---
if [ "${INSTALL_ANTHROPIC:-0}" = "1" ]; then
    pip install langchain-anthropic && echo "✅ langchain-anthropic installed"
fi
if [ "${INSTALL_OPENAI:-0}" = "1" ]; then
    pip install langchain-openai && echo "✅ langchain-openai installed"
fi
if [ "${INSTALL_GOOGLE:-0}" = "1" ]; then
    pip install langchain-google-genai && echo "✅ langchain-google-genai installed"
fi

# --- Verify import ---
echo ""
echo "Verifying installation..."
python3 -c "from deepagents import create_deep_agent, __version__; print(f'deepagents {__version__} — import OK')"

echo ""
echo "=== Setup complete ==="
echo ""
echo "Quick start:"
echo "  from deepagents import create_deep_agent"
echo "  agent = create_deep_agent()"
echo "  result = agent.invoke({'messages': [{'role': 'user', 'content': 'Hello'}]})"
echo "  print(result['messages'][-1].content)"
echo ""
echo "Docs: https://docs.langchain.com/oss/python/deepagents/overview"
