# OMG Setup & Reference Guide

> Human-facing documentation extracted from SKILL.md.
> Agent-executable instructions remain in SKILL.md.

## Quick Start

> **Source of truth**: `https://github.com/supercent-io/skills-template`
> Local paths like `~/.claude/skills/omg/` are copies installed via `npx skills add`.

```bash
# Install OMG (npx skills add — recommended)
npx skills add https://github.com/supercent-io/skills-template --skill omg

# Full install (all AI tools + all components)
bash scripts/install.sh --all

# Check status
bash scripts/check-status.sh

# Individual AI tool setup
bash scripts/setup-claude.sh      # Claude Code plugin + hooks
bash scripts/setup-codex.sh       # Codex CLI developer_instructions
bash scripts/setup-gemini.sh      # Gemini CLI hooks + GEMINI.md
bash scripts/setup-opencode.sh    # OpenCode plugin registration
```

## Installed Components

| Tool | Description | Install Command |
|------|------|-----------|
| **omc** (oh-my-claudecode) | Claude Code multi-agent orchestration | `/plugin marketplace add https://github.com/Yeachan-Heo/oh-my-claudecode` |
| **omx** | Multi-agent orchestration for OpenCode | `bunx oh-my-opencode setup` |
| **ohmg** | Multi-agent framework for Gemini CLI | `bunx oh-my-ag` |
| **bmad** | BMAD workflow orchestration | Included in skills |
| **ralph** | Self-referential completion loop | Included in omc or install separately |
| **plannotator** | Visual plan/diff review | Auto-installed during PLAN via `bash scripts/ensure-plannotator.sh` |
| **agentation** | UI annotation → agent code fix (`annotate` keyword) | `bash scripts/install.sh --with-agentation` |
| **agent-browser** | Headless browser for AI agents | `npm install -g agent-browser` |
| **playwriter** | Playwright-based browser automation (optional) | `npm install -g playwriter` |

## Platform Plugin Configuration

### Claude Code

```bash
bash scripts/setup-claude.sh
```

Config (`~/.claude/settings.json`):
```json
{
  "hooks": {
    "PermissionRequest": [{
      "matcher": "ExitPlanMode",
      "hooks": [{
        "type": "command",
        "command": "python3 ~/.claude/skills/omg/scripts/claude-plan-gate.py",
        "timeout": 1800
      }]
    }],
    "UserPromptSubmit": [{
      "matcher": "*",
      "hooks": [{
        "type": "command",
        "command": "python3 ~/.claude/skills/omg/scripts/claude-agentation-submit-hook.py",
        "timeout": 300
      }]
    }]
  },
  "mcpServers": {
    "agentation": {
      "command": "npx",
      "args": ["-y", "agentation-mcp", "server"]
    }
  }
}
```

### Codex CLI

```bash
bash scripts/setup-codex.sh
```

Config (`~/.codex/config.toml`):
```toml
developer_instructions = """
# OMG Orchestration Workflow
# ...
"""

notify = ["python3", "~/.codex/hooks/omg-notify.py"]

[tui]
notifications = ["agent-turn-complete"]
notification_method = "osc9"

[mcp_servers.agentation]
command = "npx"
args = ["-y", "agentation-mcp", "server"]
```

> `developer_instructions` must be a **top-level string**.
> Writing it as a `[developer_instructions]` table causes Codex startup failure.

### Gemini CLI

```bash
bash scripts/setup-gemini.sh
```

Config (`~/.gemini/settings.json`):
```json
{
  "hooks": {
    "AfterAgent": [{
      "matcher": "",
      "hooks": [{
        "name": "plannotator-review",
        "type": "command",
        "command": "bash ~/.gemini/hooks/omg-plannotator.sh"
      }]
    }]
  },
  "mcpServers": {
    "agentation": {
      "command": "npx",
      "args": ["-y", "agentation-mcp", "server"]
    }
  }
}
```

### OpenCode

```bash
bash scripts/setup-opencode.sh
```

Slash commands: `/omg-plan`, `/omg-exec`, `/omg-annotate`, `/omg-cleanup`

Config (`opencode.json`):
```json
{
  "mcp": {
    "agentation": {
      "type": "local",
      "command": ["npx", "-y", "agentation-mcp", "server"]
    }
  }
}
```

## Memory & State Paths

```
{worktree}/.omc/state/omg-state.json   # OMG execution state
{worktree}/.omc/plans/omg-plan.md      # Approved plan
{worktree}/.omc/logs/omg-*.log         # Execution logs
```

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS` | Enable native team orchestration | `1` |
| `PLANNOTATOR_REMOTE` | Remote mode (no auto browser open) | unset |
| `PLANNOTATOR_PORT` | Fixed plannotator port | auto |
| `OMG_MAX_ITERATIONS` | Max ralph loop iterations | `20` |
| `AGENTATION_PORT` | agentation MCP server port | `4747` |
| `AGENTATION_TIMEOUT` | annotate watch loop timeout (seconds) | `120` |

## Troubleshooting

| Issue | Solution |
|------|------|
| plannotator not running | OMG auto-runs `bash scripts/ensure-plannotator.sh`; if still fails, run `bash .agent-skills/plannotator/scripts/check-status.sh` |
| plannotator not opening in Claude Code | Hook-only. Use `EnterPlanMode` → write plan → `ExitPlanMode`; hook fires automatically |
| plannotator feedback not received | Remove `&` background → run blocking, check `/tmp/plannotator_feedback.txt` |
| Codex same plan re-reviewed | Compare `last_reviewed_plan_hash` with current `plan.md` hash; same + terminal status = skip |
| Codex startup failure | Re-run `bash scripts/setup-codex.sh`, confirm `developer_instructions` is top-level string |
| team mode not working | Run `bash scripts/setup-claude.sh`, restart, verify `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1` |
| annotate not opening | Check `curl http://localhost:4747/health` and `/sessions`. Waits for submit before polling |
| worktree conflict | `git worktree prune && git worktree list` |

## References

- [oh-my-claudecode](https://github.com/Yeachan-Heo/oh-my-claudecode)
- [plannotator](https://plannotator.ai)
- [BMAD Method](https://github.com/bmad-dev/BMAD-METHOD)
- [Agent Skills Spec](https://agentskills.io/specification)
- [agentation](https://github.com/benjitaylor/agentation)
