# oh-my-gods

<div align="center">

[![Skills](https://img.shields.io/badge/Skills-85%2B-blue?style=for-the-badge&logo=data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHZpZXdCb3g9IjAgMCAyNCAyNCI+PHBhdGggZmlsbD0id2hpdGUiIGQ9Ik0xMiAyQzYuNDggMiAyIDYuNDggMiAxMnM0LjQ4IDEwIDEwIDEwIDEwLTQuNDggMTAtMTBTMTcuNTIgMiAxMiAyem0tMiAxNWwtNS01IDEuNDEtMS40MUwxMCAxNC4xN2w3LjU5LTcuNTlMMTkgOGwtOSA5eiIvPjwvc3ZnPg==)](https://github.com/supercent-io/skills-template)
[![Platform](https://img.shields.io/badge/Platform-Claude%20%7C%20Gemini%20%7C%20Codex%20%7C%20OpenCode-orange?style=for-the-badge)](https://github.com/supercent-io/skills-template)
[![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)](LICENSE)
[![Version](https://img.shields.io/badge/Version-1.3.0-purple?style=for-the-badge)](CHANGELOG.md)
[![LangChain](https://img.shields.io/badge/LangChain-Integrated-1C3C3C?style=for-the-badge&logo=chainlink)](https://github.com/langchain-ai/langchain-skills)

</div>

```
  ██████╗ ██╗  ██╗      ███╗   ███╗██╗   ██╗      ██████╗  ██████╗ ██████╗ ███████╗
 ██╔═══██╗██║  ██║      ████╗ ████║╚██╗ ██╔╝     ██╔════╝ ██╔═══██╗██╔══██╗██╔════╝
 ██║   ██║███████║█████╗██╔████╔██║ ╚████╔╝█████╗██║  ███╗██║   ██║██║  ██║███████╗
 ██║   ██║██╔══██║╚════╝██║╚██╔╝██║  ╚██╔╝ ╚════╝██║   ██║██║   ██║██║  ██║╚════██║
 ╚██████╔╝██║  ██║      ██║ ╚═╝ ██║   ██║         ╚██████╔╝╚██████╔╝██████╔╝███████║
  ╚═════╝ ╚═╝  ╚═╝      ╚═╝     ╚═╝   ╚═╝          ╚═════╝  ╚═════╝ ╚═════╝ ╚══════╝
```

<div align="center">

**AI Agent 개발을 위한 완전한 워크플로우 & 스킬셋**

*LLM 기반 AI 에이전트 개발의 A to Z — Plan → Execute → Verify → Ship*

[Quick Start](#quick-start) · [JEO Core](#jeo--core-orchestration-skill) · [Hidden Features](#hidden-power-features) · [LangChain](#langchain-integration) · [Full Catalog](#full-skill-catalog)

</div>

---

## What is oh-my-gods?

`oh-my-gods` is a curated collection of **85+ AI agent skills** designed for LLM-based development workflows. Built around the `jeo` orchestration protocol, it provides:

- **Unified orchestration** across Claude Code, Gemini CLI, OpenAI Codex, and OpenCode
- **Plan → Execute → Verify → Cleanup** automated pipelines
- **Multi-agent team coordination** with parallel execution
- **LangChain/LangGraph integration** for framework-aware agent development

---

## Architecture

```mermaid
graph TD
    JEO["🎯 JEO\nCore Orchestration"] --> PLAN["📋 PLAN\nralph + plannotator"]
    JEO --> EXEC["⚡ EXECUTE\nteam / bmad"]
    JEO --> VERIFY["🔍 VERIFY\nagent-browser"]
    JEO --> UI["🎨 VERIFY_UI\nagentation annotate"]
    JEO --> CLEAN["🧹 CLEANUP\nworktree prune"]

    PLAN --> |"Claude Code"| OMC["omc\noh-my-claudecode"]
    PLAN --> |"Gemini CLI"| OHMG["ohmg\noh-my-gemini"]
    PLAN --> |"Codex CLI"| OMX["omx\noh-my-codex"]

    EXEC --> BMAD["bmad\nBMAD Workflow"]
    EXEC --> RALPH["ralph\nOuroboros Loop"]

    SURVEY["🔭 survey\nlandscape scan"] -.-> JEO
    FABRIC["🧵 fabric\npattern AI"] -.-> JEO
    AUTORESEARCH["🔬 autoresearch\nML experiments"] -.-> EXEC

    classDef core fill:#4A90D9,stroke:#2C5F8A,color:#fff,font-weight:bold
    classDef hidden fill:#9B59B6,stroke:#6C3483,color:#fff
    classDef platform fill:#27AE60,stroke:#1A7A40,color:#fff
    classDef support fill:#E67E22,stroke:#A85000,color:#fff

    class JEO core
    class SURVEY,FABRIC,AUTORESEARCH,BMAD,RALPH hidden
    class OMC,OHMG,OMX platform
    class PLAN,EXEC,VERIFY,UI,CLEAN support
```

---

## Quick Start

```bash
# Install all skills (recommended — 85+ skills)
npx skills add https://github.com/supercent-io/skills-template

# Install core JEO stack only
npx skills add https://github.com/supercent-io/skills-template \
  --skill jeo --skill plannotator --skill agentation --skill survey

# Install LangChain skills
npx skills add langchain-ai/langchain-skills --skill '*' --yes
```

| Platform | First Command |
|----------|--------------|
| Claude Code | `jeo "task description"` or `/omc:team "task"` |
| Gemini CLI | `/jeo "task description"` |
| Codex CLI | `/jeo "task description"` |
| OpenCode | `/jeo "task description"` |

---

## JEO — Core Orchestration Skill

> **Keyword**: `jeo` · `annotate` · `UI검토`
> **The central nervous system of oh-my-gods**

JEO orchestrates a complete, automated development pipeline across all AI agent platforms.

```
┌─────────────────────────────────────────────────────────────────┐
│                     JEO WORKFLOW                                │
├──────────┬──────────┬──────────┬──────────┬────────────────────┤
│  STEP 0  │  STEP 1  │  STEP 2  │  STEP 3  │  STEP 4            │
│ Bootstrap│   PLAN   │ EXECUTE  │  VERIFY  │  CLEANUP           │
│          │          │          │          │                    │
│ State    │ ralph    │ omc:team │ agent-   │ worktree           │
│ init     │    +     │    or    │ browser  │ prune              │
│          │ planno-  │  bmad    │    +     │                    │
│          │ tator    │          │ agenta-  │                    │
│          │          │          │ tion     │                    │
└──────────┴──────────┴──────────┴──────────┴────────────────────┘
```

### JEO State Machine

```mermaid
stateDiagram-v2
    [*] --> plan: jeo keyword detected
    plan --> execute: plan_approved = true
    plan --> plan: feedback received → revise
    execute --> verify: execution complete
    verify --> verify_ui: annotate keyword
    verify --> cleanup: no annotate
    verify_ui --> cleanup: annotations resolved
    cleanup --> [*]: phase = done

    note right of plan
        ralph + plannotator
        Visual browser review
        Hash-guarded re-review
    end note
    note right of execute
        Claude: /omc:team
        Others: /bmad workflow
    end note
    note right of verify_ui
        agentation watch loop
        Submit-gated processing
        CSS selector code fixes
    end note
```

### Platform Support

| Platform | Team Mode | PLAN Gate | VERIFY_UI | Install |
|----------|-----------|-----------|-----------|---------|
| **Claude Code** | `/omc:team` | ExitPlanMode hook | MCP tool | `bash setup-claude.sh` |
| **Gemini CLI** | `ohmg` | AfterAgent hook | HTTP REST | `bash setup-gemini.sh` |
| **Codex CLI** | `omx` | notify hook | HTTP REST | `bash setup-codex.sh` |
| **OpenCode** | `omx` | submit_plan plugin | HTTP REST | `bash setup-opencode.sh` |

---

## Hidden Power Features

> These features unlock the full potential of the oh-my-gods ecosystem.

```
╔══════════════════════════════════════════════════════════════════╗
║              HIDDEN POWER FEATURES                               ║
╠══════════════╦═══════════════════════════════════════════════════╣
║  omc         ║  Claude Code 32-agent orchestration layer        ║
║  omx         ║  OpenAI Codex multi-agent orchestration          ║
║  ohmg        ║  Gemini / Antigravity workflows (Google AI)      ║
║  bmad        ║  Structured phase-based development (BMAD)       ║
║  bmad-idea   ║  Creative AI — 5 specialist ideation agents      ║
║  survey      ║  Pre-implementation landscape scan               ║
║  autoresearch║  Autonomous overnight ML experiments (Karpathy)  ║
║  fabric      ║  AI prompt patterns & content extraction CLI     ║
║  agentation  ║  UI annotation → agent code fix (annotate)      ║
║  plannotator ║  Visual plan/diff review browser UI              ║
║  agent-browser║ Headless browser verification for AI agents     ║
║  playwriter  ║  Playwright automation with live browser         ║
╚══════════════╩═══════════════════════════════════════════════════╝
```

### Feature Details

| Skill | Keyword | Description | Source |
|-------|---------|-------------|--------|
| `omc` | `omc`, `autopilot` | 32 specialized Claude Code agents with smart model routing, persistent loops, real-time HUD | [oh-my-claudecode](https://github.com/Yeachan-Heo/oh-my-claudecode) |
| `omx` | `omx` | 40+ workflow skills, team orchestration in tmux for OpenAI Codex CLI | Internal |
| `ohmg` | `ohmg` | Google Antigravity/Gemini multi-agent framework with 6 specialist agents | Internal |
| `bmad` | `bmad`, `/workflow-init` | Analysis → Planning → Solutioning → Implementation structured phases | [BMAD Method](https://github.com/bmad-dev/BMAD-METHOD) |
| `bmad-idea` | `bmad-idea` | 5 creative specialist agents — design thinking, innovation, storytelling | Internal |
| `survey` | `survey` | Cross-platform landscape scan before planning; saves artifacts to `.survey/` | Internal |
| `autoresearch` | `autoresearch`, `val_bpb` | Karpathy-style autonomous GPU overnight experiments with git ratchet | Karpathy methodology |
| `fabric` | `fabric` | AI prompt orchestration via reusable Patterns; YouTube summaries, doc analysis | [fabric](https://github.com/danielmiessler/fabric) |
| `agentation` | `annotate`, `UI검토` | Click UI elements → AI applies targeted code fixes via CSS selectors | [agentation](https://github.com/benjitaylor/agentation) |
| `plannotator` | `plan` | Visual browser UI for reviewing AI-generated plans; approve or send feedback | [plannotator](https://plannotator.ai) |
| `agent-browser` | `agent-browser` | Headless browser snapshot & verification for AI agents | npm:agent-browser |
| `playwriter` | `playwriter` | Playwright automation connecting to your *running* browser (preserves cookies/logins) | Internal |

---

## LangChain Integration

> **Source**: [`langchain-ai/langchain-skills`](https://github.com/langchain-ai/langchain-skills/tree/main)
> MIT License — Official LangChain AI skills for agent development

oh-my-gods integrates the official LangChain skills collection, providing framework-aware guidance for building LangChain/LangGraph/Deep Agents applications.

### Installation

```bash
# Install all LangChain skills
npx skills add langchain-ai/langchain-skills --skill '*' --yes

# Or install specific skills
npx skills add langchain-ai/langchain-skills \
  --skill framework-selection \
  --skill langchain-rag \
  --skill langgraph-fundamentals \
  --skill deep-agents-core \
  --yes
```

### LangChain Skill Catalog

```mermaid
mindmap
  root((LangChain Skills))
    Getting Started
      framework-selection
        Which framework to use?
        LangChain vs LangGraph vs Deep Agents
      langchain-dependencies
        Package versions
        Python/TypeScript setup
    Deep Agents
      deep-agents-core
        create_deep_agent()
        Middleware architecture
        SKILL.md format
      deep-agents-memory
        StateBackend ephemeral
        StoreBackend persistent
        FilesystemMiddleware
      deep-agents-orchestration
        SubAgentMiddleware
        TodoListMiddleware
        HITL interrupts
    LangChain
      langchain-fundamentals
        create_agent()
        @tool decorator
        Structured output
      langchain-middleware
        HumanInTheLoopMiddleware
        Custom middleware
        Approval workflows
      langchain-rag
        Document loaders
        RecursiveCharacterTextSplitter
        Chroma / FAISS / Pinecone
    LangGraph
      langgraph-fundamentals
        StateGraph
        Nodes and edges
        Send fan-out
      langgraph-persistence
        Checkpointers
        PostgresSaver production
        Time travel
      langgraph-human-in-the-loop
        interrupt()
        Command resume
        Idempotency rules
```

### Framework Selection Guide

| Use Case | Recommended Framework |
|----------|----------------------|
| Multi-step tasks, file management, on-demand skills | **Deep Agents** |
| Complex control flow (loops, branching, parallelization) | **LangGraph** |
| Simple single-purpose agent with tools | **LangChain** `create_agent()` |
| Pure model call / retrieval pipeline | **LangChain LCEL** |

### Key Integration Scripts

```bash
# Verify LangChain environment
python3 -c "import langchain; import langgraph; print('LangChain', langchain.__version__)"

# Check required packages
pip show langchain-core langchain-community langgraph langsmith

# Quick RAG pipeline test
python3 -c "
from langchain_community.document_loaders import TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
loader = TextLoader('./README.md')
docs = loader.load()
splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
chunks = splitter.split_documents(docs)
print(f'Created {len(chunks)} chunks from README')
"
```

### Integration with JEO

When using LangChain/LangGraph within a JEO workflow:

```
jeo "build a RAG system for our docs" annotate
  │
  ▼
[PLAN] framework-selection → langgraph-fundamentals → langchain-rag
  │         (plannotator visual review)
  ▼
[EXECUTE] /omc:team 3:executor
  │   → implements StateGraph with RAG nodes
  │   → uses langchain-rag patterns
  ▼
[VERIFY_UI] annotate
  │   → agentation captures UI feedback
  └── → agent applies targeted fixes
```

---

## Full Skill Catalog

### Core Orchestration

| Skill | Keyword | Platform | Description |
|-------|---------|----------|-------------|
| `jeo` | `jeo` | All | Integrated orchestration: PLAN→EXECUTE→VERIFY→CLEANUP |
| `omc` | `omc`, `autopilot` | Claude Code | 32-agent multi-agent orchestration layer |
| `omx` | `omx` | Codex CLI | 40+ workflow skills, tmux team orchestration |
| `ohmg` | `ohmg` | Gemini CLI | Antigravity multi-agent framework |
| `ralph` | `ralph`, `ooo` | All | Ouroboros specification-first + persistent completion loop |
| `ralphmode` | `ralphmode` | All | Automation permission profiles (sandbox-first, repo boundary) |
| `bmad` | `bmad`, `/workflow-init` | All | Structured phase-based AI development |
| `bmad-idea` | `bmad-idea` | All | Creative intelligence — 5 specialist ideation agents |
| `survey` | `survey` | All | Pre-implementation landscape scan |

### Planning & Review

| Skill | Keyword | Description |
|-------|---------|-------------|
| `plannotator` | `plan` | Visual browser plan/diff review |
| `agentation` | `annotate`, `UI검토` | UI annotation → targeted code fixes |
| `agent-browser` | `agent-browser` | Headless browser verification |
| `playwriter` | `playwriter` | Playwright with live browser (cookies preserved) |
| `vibe-kanban` | `kanbanview` | Visual Kanban board for agent tasks |

### Development Workflow

| Skill | Description |
|-------|-------------|
| `agent-development-principles` | Universal AI collaboration principles (divide-and-conquer, context management) |
| `agent-principles` | Core principles for AI agent collaboration |
| `agent-workflow` | Daily workflow optimization: shortcuts, Git, MCP, sessions |
| `agent-configuration` | Agent policy, security, hooks/skills/plugins setup |
| `agent-evaluation` | Comprehensive agent evaluation system design |
| `git-workflow` | Commit, branch, merge, PR workflows |
| `git-submodule` | Git submodule management |
| `debugging` | Root cause analysis, regression isolation |
| `code-review` | Comprehensive code review with API contracts |

### Backend & Infrastructure

| Skill | Description |
|-------|-------------|
| `api-design` | RESTful and GraphQL API design |
| `api-documentation` | OpenAPI/Swagger docs generation |
| `authentication-setup` | JWT, OAuth, session management |
| `backend-testing` | Unit/integration/API test strategies |
| `database-schema-design` | SQL/NoSQL schema design and optimization |
| `deployment-automation` | CI/CD, Docker/Kubernetes, cloud infrastructure |
| `environment-setup` | Dev/staging/production environment config |
| `monitoring-observability` | Health checks, metrics, log aggregation |
| `security-best-practices` | OWASP Top 10, RBAC, API security |

### Frontend & Design

| Skill | Description |
|-------|-------------|
| `design-system` | Design tokens, layout rules, motion guidance |
| `frontend-design-system` | Production-grade UI with accessibility |
| `responsive-design` | Mobile-first layouts, breakpoints |
| `ui-component-patterns` | Reusable component libraries |
| `react-best-practices` | React/Next.js performance optimization |
| `vercel-react-best-practices` | Vercel Engineering React guidelines |
| `state-management` | Redux, Context, Zustand patterns |
| `web-accessibility` | WCAG 2.1 compliance |
| `web-design-guidelines` | Web Interface Guidelines compliance review |

### AI & Data

| Skill | Description |
|-------|-------------|
| `autoresearch` | Autonomous ML experiments (Karpathy methodology) |
| `fabric` | AI prompt patterns — YouTube summaries, doc analysis |
| `genkit` | Firebase Genkit AI flows and RAG pipelines |
| `firebase-ai-logic` | Gemini in Firebase integration |
| `data-analysis` | Dataset analysis, visualizations, statistics |
| `llm-monitoring-dashboard` | LLM usage monitoring page generator |
| `ai-tool-compliance` | Internal AI tool compliance automation (P0/P1) |
| `opencontext` | Persistent memory and context management |
| `prompt-repetition` | LLM accuracy via prompt repetition technique |

### Content & Media

| Skill | Description |
|-------|-------------|
| `presentation-builder` | HTML slides with `slides-grab`, export to PPTX/PDF |
| `video-production` | Remotion-based programmable video production |
| `image-generation` | Image generation via Gemini/compatible APIs |
| `pollinations-ai` | Free image generation (no API key needed) |
| `marketing-automation` | 23 sub-skills: CRO, copywriting, SEO, growth |

### LangChain / LangGraph (from langchain-ai/langchain-skills)

| Skill | Trigger | Description |
|-------|---------|-------------|
| `framework-selection` | "which framework", "LangChain vs" | Choose LangChain/LangGraph/Deep Agents |
| `langchain-dependencies` | "install langchain", "package versions" | Package setup and version management |
| `langchain-fundamentals` | "langchain agent", "create_agent" | Agent creation, tools, HITL patterns |
| `langchain-middleware` | "human in the loop", "approval workflow" | HITL approval, custom middleware |
| `langchain-rag` | "RAG", "retrieval", "vector store" | Complete RAG pipeline implementation |
| `langgraph-fundamentals` | "langgraph", "StateGraph" | Graph nodes, edges, streaming |
| `langgraph-persistence` | "persist state", "checkpointer" | State persistence, PostgresSaver |
| `langgraph-human-in-the-loop` | "interrupt", "pause for approval" | HITL patterns, idempotency |
| `deep-agents-core` | "deep agent", "create_deep_agent" | Deep Agents architecture & middleware |
| `deep-agents-memory` | "agent memory", "StoreBackend" | Memory, persistence, filesystem |
| `deep-agents-orchestration` | "subagent", "todo list", "HITL" | Subagents, task planning, approval |

---

## Installation Reference

### Full Install (Recommended)

```bash
# Wipe and reinstall everything clean
npx skills add https://github.com/supercent-io/skills-template \
  --skill agent-configuration --skill agent-evaluation \
  --skill agent-development-principles --skill agent-principles \
  --skill agent-workflow --skill bmad \
  --skill bmad-gds --skill bmad-idea \
  --skill prompt-repetition --skill api-design \
  --skill api-documentation --skill authentication-setup \
  --skill backend-testing --skill database-schema-design \
  --skill design-system --skill frontend-design-system \
  --skill react-best-practices --skill vercel-react-best-practices \
  --skill responsive-design --skill state-management \
  --skill ui-component-patterns --skill web-accessibility \
  --skill web-design-guidelines --skill code-refactoring \
  --skill code-review --skill debugging \
  --skill performance-optimization --skill testing-strategies \
  --skill deployment-automation --skill firebase-ai-logic \
  --skill genkit --skill monitoring-observability \
  --skill security-best-practices --skill environment-setup \
  --skill vercel-deploy --skill changelog-maintenance \
  --skill presentation-builder --skill technical-writing \
  --skill user-guide-writing --skill sprint-retrospective \
  --skill standup-meeting --skill task-estimation \
  --skill task-planning --skill codebase-search \
  --skill data-analysis --skill log-analysis \
  --skill pattern-detection --skill llm-monitoring-dashboard \
  --skill image-generation --skill pollinations-ai \
  --skill video-production --skill marketing-automation \
  --skill agent-browser --skill agentation \
  --skill ai-tool-compliance --skill file-organization \
  --skill git-submodule --skill git-workflow --skill jeo \
  --skill ohmg --skill omx --skill omc \
  --skill opencontext --skill plannotator --skill playwriter \
  --skill ralph --skill ralphmode --skill skill-standardization \
  --skill survey --skill vibe-kanban --skill workflow-automation \
  --skill fabric --skill autoresearch

# Also install LangChain skills
npx skills add langchain-ai/langchain-skills --skill '*' --yes
```

### Platform-Specific Setup

```bash
# Claude Code (oh-my-claudecode)
/plugin marketplace add https://github.com/Yeachan-Heo/oh-my-claudecode
/omc:omc-setup
bash ~/.agent-skills/jeo/scripts/setup-claude.sh

# Gemini CLI
bash ~/.agent-skills/jeo/scripts/setup-gemini.sh
gemini extensions install https://github.com/supercent-io/skills-template

# Codex CLI
bash ~/.agent-skills/jeo/scripts/setup-codex.sh

# OpenCode
bash ~/.agent-skills/jeo/scripts/setup-opencode.sh
```

---

## Environment Requirements

```bash
# Required
node >= 18
git
bash

# Optional (platform-specific)
bun            # faster installs
docker         # container workflow
npx agentation-mcp server  # UI annotation
npm install -g agent-browser  # browser verification
```

---

## References & Sources

| Component | Source | License |
|-----------|--------|---------|
| `jeo` | [supercent-io/skills-template](https://github.com/supercent-io/skills-template) | MIT |
| `omc` | [Yeachan-Heo/oh-my-claudecode](https://github.com/Yeachan-Heo/oh-my-claudecode) | MIT |
| `ralph` | [Q00/ouroboros](https://github.com/Q00/ouroboros) | MIT |
| `plannotator` | [backnotprop/plannotator](https://plannotator.ai) | MIT |
| `bmad` | [bmad-dev/BMAD-METHOD](https://github.com/bmad-dev/BMAD-METHOD) | MIT |
| `agentation` | [benjitaylor/agentation](https://github.com/benjitaylor/agentation) | MIT |
| `fabric` | [danielmiessler/fabric](https://github.com/danielmiessler/fabric) | MIT |
| `autoresearch` | Andrej Karpathy methodology | — |
| LangChain skills | [langchain-ai/langchain-skills](https://github.com/langchain-ai/langchain-skills) | MIT |
| `agent-development-principles` | [ykdojo/claude-code-tips](https://github.com/ykdojo/claude-code-tips) + Ado Kukic | MIT |
| Agent Skills Spec | [agentskills.io](https://agentskills.io/specification) | — |

---

<div align="center">

Made with ❤️ by [supercent-io](https://github.com/supercent-io)

⭐ If this helps you, please star the repository!

```bash
gh api --silent --method PUT /user/starred/supercent-io/skills-template >/dev/null 2>&1
```

</div>
