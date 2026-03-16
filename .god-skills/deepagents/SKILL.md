---
name: deepagents
description: >
  Build production-ready AI agents using LangChain's deepagents — a batteries-included agent harness
  built on LangGraph. Use when creating AI agents with create_deep_agent(), adding composable middleware
  stacks (filesystem, memory, summarization, skills), orchestrating sub-agents, configuring backends,
  or building HITL approval workflows. Triggers on: deep agent, create_deep_agent, langchain agent
  harness, deepagents middleware, SubAgentMiddleware, FilesystemMiddleware, MemoryMiddleware,
  deep-agents SDK, LangGraph agent harness, agentic harness, batteries-included agent.
license: MIT
compatibility: >
  Requires Python >=3.11. Install via `pip install deepagents` or `uv add deepagents`.
  Works with any tool-calling LLM (Claude, GPT-4o, Gemini via provider:model format).
  LangGraph-native — compatible with LangGraph Studio, streaming, and checkpointers.
  Optional MCP integration: `pip install langchain-mcp-adapters`.
metadata:
  version: "1.0"
  source: langchain-ai/deepagents
  tags: langchain, langgraph, deep-agents, ai-agent, middleware, subagents, python, production
allowed-tools: Bash Read Write Edit Glob Grep
---

# deepagents — Batteries-Included LangGraph Agent Harness

`deepagents` is an opinionated, production-ready AI agent framework built on LangGraph. Inspired by Claude Code, it provides immediate agent capabilities without requiring manual assembly of prompts, tools, and context management. Returns a compiled LangGraph graph — works natively with streaming, LangGraph Studio, and checkpointers.

## When to use this skill

- Building a Python AI agent that needs file access, shell execution, and todo management out of the box
- Adding memory, skills, or sub-agent orchestration via composable middleware
- Integrating HITL (Human-in-the-Loop) approval workflows before destructive operations
- Replacing manual LangGraph `StateGraph` assembly with a pre-wired harness
- Using any tool-calling model (Claude, GPT-4o, Gemini) with a unified `provider:model` interface
- Deploying agents to LangGraph Cloud / LangGraph Studio

## Installation

```bash
pip install deepagents
# or (recommended)
uv add deepagents
```

Optional — MCP tool integration:

```bash
pip install langchain-mcp-adapters
```

Run the setup script for environment validation:

```bash
bash scripts/setup.sh
```

## Core API

### `create_deep_agent()` — primary entry point

Returns a **compiled LangGraph graph**.

```python
from deepagents import create_deep_agent

agent = create_deep_agent(
    model="anthropic:claude-sonnet-4-6",   # default; any tool-calling model
    tools=[...],                            # additional custom tools
    system_prompt="...",                    # prepended to base prompt
    middleware=[...],                       # AgentMiddleware instances
    subagents=[...],                        # SubAgent | CompiledSubAgent list
    skills=["path/to/skills.md"],           # skill source file paths
    memory=["AGENTS.md"],                   # persistent memory files
    response_format=None,                   # Pydantic model for structured output
    checkpointer=None,                      # LangGraph checkpointer
    backend=None,                           # BackendProtocol or BackendFactory
    interrupt_on=None,                      # tool-specific HITL pause config
    debug=False,
    name="deep-agent",
)
```

**Model format**: `"provider:model-name"` — e.g.:
- `"anthropic:claude-sonnet-4-6"` (default)
- `"openai:gpt-4o"`
- `"google_genai:gemini-2.5-pro"`

### Invocation

```python
# Standard invoke
result = agent.invoke({"messages": [{"role": "user", "content": "List Python files here"}]})
print(result["messages"][-1].content)

# Streaming (recommended for responsive UIs)
for chunk in agent.stream({"messages": [...]}):
    print(chunk)

# Async
result = await agent.ainvoke({"messages": [...]})
```

## Built-in Tools

Always available without configuration:

| Tool | Description |
|------|-------------|
| `write_todos` | Write a structured todo list for planning |
| `read_file` | Read file contents with pagination (offset/limit) |
| `write_file` | Create new files |
| `edit_file` | String-replacement editing |
| `ls` | List directory contents |
| `glob` | Find files matching glob patterns |
| `grep` | Search file contents |
| `execute` | Run shell commands (sandboxable) |
| `task` | Delegate to a sub-agent (added by SubAgentMiddleware) |

## Middleware Stack

Middleware intercepts every LLM request to inject system prompt additions, filter tools, or manage cross-turn state — without the consumer needing to wire it up.

### Default pipeline (auto-applied in order)

| # | Middleware | What it does |
|---|-----------|--------------|
| 1 | `TodoListMiddleware` | Manages structured todo lists across turns |
| 2 | `FilesystemMiddleware` | Exposes file tools (read/write/edit/ls/glob/grep) |
| 3 | `SummarizationMiddleware` | Auto-summarizes long conversations to prevent context overflow |
| 4 | `AnthropicPromptCachingMiddleware` | Caches system prompts for Anthropic models (cost savings) |
| 5 | `PatchToolCallsMiddleware` | Normalizes tool call formats across providers |

### Optional middleware

```python
from deepagents import (
    FilesystemMiddleware,
    MemoryMiddleware,
    SubAgentMiddleware,
    SubAgent,
)

agent = create_deep_agent(
    middleware=[
        # Inject AGENTS.md into system prompt at every turn
        MemoryMiddleware(memory_files=["AGENTS.md", "SKILLS.md"]),

        # Add sub-agent task delegation via `task` tool
        SubAgentMiddleware(subagents=[
            SubAgent(
                name="researcher",
                description="Searches the web and summarizes findings",
                system_prompt="You are a research specialist...",
                tools=[web_search_tool],
            )
        ]),
    ]
)
```

## SubAgent Interface

```python
from deepagents import SubAgent, CompiledSubAgent

# TypedDict spec — define inline, pass to SubAgentMiddleware
researcher = SubAgent(
    name="researcher",                          # required
    description="Searches web for information", # required
    system_prompt="You are a researcher...",    # required
    tools=[web_search, fetch_url],              # optional
    model="anthropic:claude-haiku-4-5",         # optional model override
    middleware=[...],                           # optional
    skills=["research-skills.md"],              # optional
)

# Pre-compiled — bring your own LangGraph runnable
custom = CompiledSubAgent(
    name="custom",
    description="Custom compiled subagent",
    runnable=my_compiled_graph,   # must include 'messages' in state schema
)
```

## Backends

Backends control file storage and shell execution. Use `CompositeBackend` to route operations by path prefix.

```python
from deepagents.backends import (
    FilesystemBackend,
    LocalShellBackend,
    SandboxBackend,
    StoreBackend,
    CompositeBackend,
)

# Route /memories/ to persistent store, everything else to local filesystem
backend = CompositeBackend(
    routes={"/memories/": StoreBackend(store=my_store)},
    default=FilesystemBackend(root_dir="/workspace"),
)

agent = create_deep_agent(backend=backend)
```

## HITL (Human-in-the-Loop)

Pause execution before specific tools to require human approval:

```python
agent = create_deep_agent(
    checkpointer=MemorySaver(),   # required for HITL state persistence
    interrupt_on={
        "execute": True,          # pause before every shell command
        "write_file": True,       # pause before every file write
    }
)

# Agent pauses at `execute` — inspect, then resume:
result = agent.invoke(
    {"messages": [{"role": "user", "content": "Deploy to production"}]},
    config={"configurable": {"thread_id": "session-1"}},
)
# Resume after human approval:
result = agent.invoke(None, config={"configurable": {"thread_id": "session-1"}})
```

## Examples

### Example 1: Minimal agent (zero config)

```python
from deepagents import create_deep_agent

agent = create_deep_agent()
result = agent.invoke({"messages": [{"role": "user", "content": "List all Python files here"}]})
print(result["messages"][-1].content)
```

### Example 2: Agent with custom tools and memory

```python
from deepagents import create_deep_agent, MemoryMiddleware
from langchain_core.tools import tool

@tool
def search_web(query: str) -> str:
    """Search the web for information."""
    # ...implementation
    return results

agent = create_deep_agent(
    model="anthropic:claude-sonnet-4-6",
    tools=[search_web],
    middleware=[MemoryMiddleware(memory_files=["AGENTS.md"])],
    system_prompt="You are a research assistant with web access.",
)
```

### Example 3: Multi-agent deep research

```python
from deepagents import create_deep_agent, SubAgentMiddleware, SubAgent

web_agent = SubAgent(
    name="web_researcher",
    description="Searches the web and extracts relevant information",
    system_prompt="Search comprehensively and return structured findings.",
    tools=[tavily_search],
)

analyst = SubAgent(
    name="analyst",
    description="Analyzes data and produces structured reports",
    system_prompt="Analyze data rigorously and produce evidence-backed reports.",
)

orchestrator = create_deep_agent(
    model="anthropic:claude-sonnet-4-6",
    middleware=[SubAgentMiddleware(subagents=[web_agent, analyst])],
    system_prompt="Orchestrate research tasks across specialist agents.",
)
```

### Example 4: Structured output

```python
from pydantic import BaseModel
from deepagents import create_deep_agent

class ResearchReport(BaseModel):
    title: str
    summary: str
    key_findings: list[str]
    sources: list[str]

agent = create_deep_agent(response_format=ResearchReport)
result = agent.invoke({"messages": [{"role": "user", "content": "Research deepagents framework"}]})
# result["messages"][-1] contains a structured ResearchReport
```

### Example 5: Skills injection

```python
# skills.md defines callable skills as markdown
agent = create_deep_agent(
    skills=["~/.agent-skills/deepagents/references/deepagents-api.md"],
    system_prompt="Use skills when available before writing new code.",
)
```

## Best practices

1. **Start minimal** — `create_deep_agent()` with no args gives a working filesystem agent immediately
2. **Use middleware composition** — add only the middleware you need; avoid duplicating the default stack
3. **Scope subagent tools** — give each subagent only the tools it needs to reduce hallucination risk
4. **Leverage MemoryMiddleware** — inject `AGENTS.md` for project context instead of bloating system prompts
5. **Use CompositeBackend** — separate ephemeral scratch space from persistent memory directories
6. **Stream by default** — use `agent.stream()` for responsive UIs and long-running tasks
7. **Pin provider packages** — pin `langchain-anthropic`, `langchain-openai` versions to avoid breaking changes
8. **HITL for destructive ops** — always `interrupt_on={"execute": True}` in production agentic pipelines

## Framework selection guide

| Use case | Recommended |
|----------|-------------|
| Multi-step tasks, file management, on-demand skills | **deepagents** (`create_deep_agent`) |
| Complex control flow (loops, branching, parallelization) | **LangGraph** (`StateGraph`) |
| Simple single-purpose agent with tools | **LangChain** (`create_react_agent`) |
| Pure model call / retrieval pipeline | **LangChain LCEL** |

## References

- [GitHub: langchain-ai/deepagents](https://github.com/langchain-ai/deepagents)
- [PyPI: deepagents](https://pypi.org/project/deepagents/)
- [LangChain Documentation](https://docs.langchain.com/oss/python/deepagents/overview)
- [API Reference](https://reference.langchain.com/python/deepagents/)
- [Examples directory](https://github.com/langchain-ai/deepagents/tree/main/examples)
- [AGENTS.md monorepo guidelines](https://github.com/langchain-ai/deepagents/blob/main/AGENTS.md)
- See `references/deepagents-api.md` for full API reference
