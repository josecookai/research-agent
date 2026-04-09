# Research Agent

Autonomous research agents built with [Claude Managed Agents](https://platform.claude.com/docs/en/managed-agents/overview.md).

## Projects

### 1. Generic Research Report (`run.py`)

Given a topic, one agent searches the web and pushes a Markdown report to GitHub.

```bash
python run.py "AI Agent market landscape 2025" josecookai/research-reports main
```

### 2. AGI Economic Impact — Red/Blue Team Debate (`agi_debate/`)

**Multi-agent orchestration**: 4 specialized agents collaborate across 6 phases:

```
Phase 1  Researcher      1 session   — 20+ web searches across economic literature
Phase 2  Opening Args    2 parallel  — Blue Team (optimist) vs Red Team (pessimist)
Phase 3  Rebuttals       2 parallel  — Each team counters the other's arguments
Phase 4  Closing         2 parallel  — Cross-examination + probability estimates
Phase 5  Synthesis       1 session   — Final comprehensive report (~5,000 words)
Phase 6  Push                        — git commit + push to GitHub
```

**Topics covered:** unemployment scenarios, GDP projections, social unrest risk, US stock market (top 10 winners + losers).

```bash
# One-time: create the 4 agents
python agi_debate/setup.py

# Run the full debate + push report
python agi_debate/orchestrate.py
```

Reports land in `reports/agi-debate-YYYY-MM-DD/`.

## How It Works

Uses the **Anthropic Managed Agents API** — Anthropic hosts the agent loop and provisions a sandboxed container per session where tools execute autonomously.

```
Orchestrator (your script)
    │
    ├─ Session 1: Researcher ──► web_search × 20 ──► research_brief.md
    │
    ├─ Session 2: Blue Team ──┐  (parallel)
    ├─ Session 3: Red Team  ──┘  web_search + structured argument
    │
    ├─ Session 4: Blue Team ──┐  (parallel, given opponent's Round 1)
    ├─ Session 5: Red Team  ──┘
    │
    ├─ Session 6: Blue Team ──┐  (parallel, full debate context)
    ├─ Session 7: Red Team  ──┘
    │
    └─ Session 8: Synthesizer ──► agi_impact_report.md ──► git push
```

## Setup

```bash
pip install -r requirements.txt
cp .env.example .env
# fill in ANTHROPIC_API_KEY and GITHUB_TOKEN
```

## File Structure

| Path | Purpose |
|------|---------|
| `setup.py` | One-time: create generic research agent |
| `run.py` | Per-task: single-agent research + push |
| `vault_setup.py` | Optional: GitHub OAuth for PR creation |
| `agi_debate/setup.py` | One-time: create 4 AGI debate agents |
| `agi_debate/orchestrate.py` | Run full 8-session debate pipeline |
| `agi_debate/utils.py` | `run_session()` helper |
| `reports/` | Generated debate reports (pushed to GitHub) |

## Why Managed Agents?

| Capability | Messages API | Managed Agents |
|---|---|---|
| Agent loop | Write your own | Built-in |
| Tool execution | Handle manually | Server-side in container |
| Parallel agents | Complex threading | `ThreadPoolExecutor` + independent sessions |
| Long-running tasks | Timeout risk | No timeout |
| File system | None | Real container with bash + git |
