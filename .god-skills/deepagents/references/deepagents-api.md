# deepagents — Full API Reference

> Source: [langchain-ai/deepagents](https://github.com/langchain-ai/deepagents) · Version: 0.4.11 · License: MIT

---

## Package Layout

```
libs/
├── deepagents/        # Core SDK — pip install deepagents
├── cli/               # deepagents-cli terminal UI tool
├── acp/               # Agent Context Protocol support
├── harbor/            # Evaluation/benchmark framework
└── partners/          # Integration packages (daytona, etc.)
```

Internal SDK structure (`libs/deepagents/deepagents/`):

```
deepagents/
├── __init__.py          # Public exports
├── _models.py           # Model resolution utilities
├── _version.py          # Version string
├── base_prompt.md       # Default system prompt
├── graph.py             # create_deep_agent() entry point
├── backends/
│   ├── protocol.py      # BackendProtocol, SandboxBackendProtocol
│   ├── composite.py     # CompositeBackend — path-prefix routing
│   ├── filesystem.py    # FilesystemBackend
│   ├── local_shell.py   # LocalShellBackend
│   ├── sandbox.py       # SandboxBackend
│   ├── state.py         # StateBackend
│   └── store.py         # StoreBackend
└── middleware/
    ├── filesystem.py    # FilesystemMiddleware
    ├── subagents.py     # SubAgentMiddleware, SubAgent, CompiledSubAgent
    ├── memory.py        # MemoryMiddleware
    ├── skills.py        # SkillsMiddleware
    ├── summarization.py # SummarizationMiddleware
    └── patch_tool_calls.py
```

---

## Public API (`__init__.py`)

```python
from deepagents import (
    __version__,           # "0.4.11"
    create_deep_agent,     # Primary entry point — returns compiled LangGraph graph
    FilesystemMiddleware,
    MemoryMiddleware,
    SubAgentMiddleware,
    SubAgent,              # TypedDict spec for defining a subagent inline
    CompiledSubAgent,      # Pre-compiled subagent with custom LangGraph runnable
)
```

---

## `create_deep_agent()` — Full Signature

```python
def create_deep_agent(
    *,
    model: str | BaseChatModel = "anthropic:claude-sonnet-4-6",
    tools: Sequence[BaseTool | Callable | dict] = (),
    system_prompt: str = "",
    middleware: list[AgentMiddleware] = (),
    subagents: list[SubAgent | CompiledSubAgent] = (),
    skills: list[str] = (),
    memory: list[str] = (),
    response_format: type[BaseModel] | None = None,
    checkpointer: BaseCheckpointSaver | None = None,
    backend: BackendProtocol | BackendFactory | None = None,
    interrupt_on: dict[str, bool | InterruptOnConfig] | None = None,
    debug: bool = False,
    name: str = "deep-agent",
    cache: BaseCache | None = None,
) -> CompiledGraph:
```

All parameters are **keyword-only**. New parameters added in future versions will never break existing calls.

### Parameter reference

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `model` | `str \| BaseChatModel` | `"anthropic:claude-sonnet-4-6"` | LLM to use. String format: `"provider:model-name"` |
| `tools` | `Sequence` | `()` | Additional tools beyond the built-in set |
| `system_prompt` | `str` | `""` | Prepended to the base system prompt |
| `middleware` | `list` | `()` | Composable middleware stack |
| `subagents` | `list` | `()` | Sub-agent definitions (adds `task` tool) |
| `skills` | `list[str]` | `()` | Paths to SKILL.md-format files to inject |
| `memory` | `list[str]` | `()` | Paths to memory files (e.g., `AGENTS.md`) injected via MemoryMiddleware |
| `response_format` | `BaseModel \| None` | `None` | Pydantic model for structured output |
| `checkpointer` | `BaseCheckpointSaver \| None` | `None` | LangGraph checkpointer — required for HITL and state persistence |
| `backend` | `BackendProtocol \| None` | `None` | Custom file/shell backend |
| `interrupt_on` | `dict \| None` | `None` | Tools that trigger HITL pauses |
| `debug` | `bool` | `False` | Enable verbose LangGraph debug output |
| `name` | `str` | `"deep-agent"` | Graph name (used in LangGraph Studio) |
| `cache` | `BaseCache \| None` | `None` | LLM response cache |

---

## Model Resolution

```python
# Provider format: "provider:model-name"
resolve_model("anthropic:claude-sonnet-4-6")  # -> ChatAnthropic
resolve_model("openai:gpt-4o")                # -> ChatOpenAI (uses Responses API)
resolve_model("google_genai:gemini-2.5-pro")  # -> ChatGoogleGenerativeAI

get_model_identifier(model)        # extracts "model_name" or "model" from config
model_matches_spec(model, spec)    # exact or partial provider:model match
```

---

## SubAgent TypedDict

```python
class SubAgent(TypedDict, total=False):
    name: str                                       # required
    description: str                                # required
    system_prompt: str                              # required
    tools: Sequence[BaseTool | Callable | dict]     # optional
    model: str | BaseChatModel                      # optional override
    middleware: list[AgentMiddleware]               # optional
    interrupt_on: dict[str, bool | InterruptOnConfig]  # optional
    skills: list[str]                               # optional

class CompiledSubAgent(TypedDict):
    name: str
    description: str
    runnable: Runnable    # must include 'messages' in state schema
```

---

## BackendProtocol Interface

```python
class BackendProtocol:
    # All methods have async a* variants
    def ls_info(path: str) -> list[FileInfo]: ...
    def read(file_path: str, offset: int, limit: int) -> bytes: ...
    def grep_raw(pattern: str, path: str, glob: str) -> list[GrepMatch]: ...
    def glob_info(pattern: str, path: str) -> list[FileInfo]: ...
    def write(file_path: str, content: bytes) -> WriteResult: ...
    def edit(file_path: str, old_string: str, new_string: str, replace_all: bool) -> EditResult: ...
    def upload_files(files: ...) -> list[FileUploadResponse]: ...
    def download_files(paths: ...) -> list[FileDownloadResponse]: ...

class SandboxBackendProtocol(BackendProtocol):
    id: str   # unique sandbox identifier
    def execute(command: str, timeout: float) -> ExecuteResponse: ...
```

---

## Default System Prompt

```
You are a Deep Agent, an AI assistant that helps users accomplish tasks using tools.

## Core Behavior
- Be concise and direct. Don't over-explain unless asked.
- NEVER add unnecessary preamble ("Sure!", "Great question!", "I'll now...").
- Don't say "I'll now do X" — just do it.
- If the request is ambiguous, ask questions before acting.

## Doing Tasks
1. Understand first — read relevant files, check existing patterns.
2. Act — implement the solution.
3. Verify — check your work against what was asked, not against your own output.

Keep working until the task is fully complete. Only yield back to the user when done or genuinely blocked.
```

Custom `system_prompt` is **prepended** to this base prompt.

---

## Available Examples

| Example | Description |
|---------|-------------|
| `examples/deep_research/` | Multi-step web research with Tavily + parallel sub-agents + reflection |
| `examples/content-builder-agent/` | Memory + skills + subagents for structured writing |
| `examples/text-to-sql-agent/` | Natural language to SQL with planning and skills injection |
| `examples/ralph_mode/` | Autonomous looping with filesystem persistence |
| `examples/downloading_agents/` | Agents as downloadable folder artifacts |
| `examples/nvidia_deep_agent/` | NVIDIA-specific agent configuration |

---

## CLI Tool (`deepagents-cli`)

Separate package with terminal UI (Textual-based). Provides:
- Web search integration
- Remote sandboxes
- Persistent memory
- Human-in-the-loop approval workflows

Install via shell script (see repository for latest URL).

---

## Dependencies

```toml
# Runtime
langchain-core>=1.2.18,<2.0.0
langchain>=1.2.11,<2.0.0
langchain-anthropic>=1.3.4,<2.0.0
langchain-google-genai>=4.2.0,<5.0.0
wcmatch

# Optional
langchain-mcp-adapters   # MCP tool integration
```

---

## Version Notes

- **Current**: `0.4.11` (Beta — Development Status 4)
- **Python**: `>=3.11,<4.0`
- `SubAgentMiddleware` deprecated kwargs (`default_model`, `default_tools`, `default_middleware`, `default_interrupt_on`, `general_purpose_agent`) — removal scheduled in **0.5.0**. Use `backend` and fully-specified `subagents` instead.
- TypeScript/JavaScript version of deepagents also available in the repository.
