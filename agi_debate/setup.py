"""
ONE-TIME SETUP — creates 4 specialized agents for AGI debate.
Run once; saves all IDs to .env.

Agents:
  agi-researcher   — deep web research (20+ searches)
  agi-blue-team    — optimist debater
  agi-red-team     — pessimist debater
  agi-synthesizer  — final report writer (writes to /mnt/session/outputs/)
"""
import anthropic
from dotenv import set_key

client = anthropic.Anthropic()
ENV_FILE = ".env"


# ── Environment (shared) ──────────────────────────────────
print("Creating shared environment...")
env = client.beta.environments.create(
    name="agi-debate-env",
    config={"type": "cloud", "networking": {"type": "unrestricted"}},
)
print(f"  ENV_ID_AGI = {env.id}")


# ── Agent 1: Researcher ───────────────────────────────────
print("Creating researcher agent...")
researcher = client.beta.agents.create(
    name="AGI Impact Researcher",
    model="claude-opus-4-6",
    system="""You are a rigorous economic research analyst specializing in technological disruption.

Conduct thorough, multi-angle web research. Search at least 20 times covering:
- Peer-reviewed studies and think-tank reports (WEF, McKinsey, Oxford, IMF, Goldman Sachs)
- Historical analogies: Industrial Revolution, agricultural mechanization, computerization
- Quantitative data: unemployment projections, GDP forecasts, Gini coefficient trends
- AGI timeline estimates (expert surveys, Metaculus, Epoch AI)
- Specific sectors and job categories at risk
- US stock market historical patterns during tech disruptions

Always cite sources with full URLs. Be comprehensive, factual, and data-driven.
Output a structured research brief with numbered findings and source links.""",
    tools=[{
        "type": "agent_toolset_20260401",
        "default_config": {"enabled": True},
        "configs": [
            {"name": "bash",  "enabled": False},
            {"name": "write", "enabled": False},
            {"name": "edit",  "enabled": False},
        ],
    }],
)
print(f"  RESEARCHER_AGENT_ID = {researcher.id}")


# ── Agent 2: Blue Team (Optimist) ────────────────────────
print("Creating blue team agent...")
blue_team = client.beta.agents.create(
    name="AGI Blue Team — Optimist",
    model="claude-opus-4-6",
    system="""You are the BLUE TEAM in a structured Red Team / Blue Team policy debate.

Your mandate: argue that AGI's economic impact will be NET POSITIVE.

Core positions to defend:
- Net job creation: every prior technology wave created more jobs than it destroyed
- GDP growth: unprecedented productivity gains → wealth for more people
- Social stability: higher GDP funds safety nets and managed transitions
- US stocks: identify specific beneficiary sectors and companies with conviction

Debate methodology:
- Use data, historical analogies, and economic models
- Steel-man the opposing view before refuting it
- Be specific: timelines, percentage estimates, named companies
- Structure with clear headers, tables, and bullet points
- Supplement your arguments with web searches when needed""",
    tools=[{
        "type": "agent_toolset_20260401",
        "default_config": {"enabled": False},
        "configs": [
            {"name": "web_search", "enabled": True},
            {"name": "web_fetch",  "enabled": True},
        ],
    }],
)
print(f"  BLUE_TEAM_AGENT_ID = {blue_team.id}")


# ── Agent 3: Red Team (Pessimist) ────────────────────────
print("Creating red team agent...")
red_team = client.beta.agents.create(
    name="AGI Red Team — Pessimist",
    model="claude-opus-4-6",
    system="""You are the RED TEAM in a structured Red Team / Blue Team policy debate.

Your mandate: argue that AGI's economic impact will be NET NEGATIVE / HIGHLY DISRUPTIVE.

Core positions to defend:
- Structural unemployment: AGI automates cognitive work — qualitatively different from past tech
- GDP concentration: gains captured by capital → extreme inequality → political instability
- Social unrest risk: historical parallels (Luddites 1811, Great Depression, deindustrialization)
- US stocks: identify sectors and companies facing existential disruption

Debate methodology:
- Use data, historical analogies, and economic models
- Steel-man the opposing view before refuting it
- Be specific: timelines, percentage estimates, named companies
- Structure with clear headers, tables, and bullet points
- Supplement your arguments with web searches when needed""",
    tools=[{
        "type": "agent_toolset_20260401",
        "default_config": {"enabled": False},
        "configs": [
            {"name": "web_search", "enabled": True},
            {"name": "web_fetch",  "enabled": True},
        ],
    }],
)
print(f"  RED_TEAM_AGENT_ID = {red_team.id}")


# ── Agent 4: Synthesizer ──────────────────────────────────
print("Creating synthesizer agent...")
synthesizer = client.beta.agents.create(
    name="AGI Impact Synthesizer",
    model="claude-opus-4-6",
    system="""You are a senior analyst at a flagship global policy institution.

Your role: synthesize research and a multi-round debate into a comprehensive, publication-quality report.

MANDATORY: save the final report to /mnt/session/outputs/agi_impact_report.md

Report structure (follow exactly):
1. Executive Summary (3 scenarios + probabilities, ~500 words)
2. Methodology (research sources, debate structure)
3. Research Findings (key data with citations)
4. Debate Summary Table (Blue vs Red, topic by topic)
5. Unemployment Analysis (3 scenarios: optimistic / base / pessimistic with timelines)
6. GDP Impact (10-year projections, distribution effects, country comparisons)
7. Social Stability & Unrest Risk (historical risk matrix, current factors)
8. US Stock Market Analysis
   - Macro impact assessment
   - Top 10 Beneficiary Companies (table: name, sector, thesis, estimated upside)
   - Top 10 At-Risk Companies (table: name, sector, thesis, estimated downside)
   - Sector rotation framework
9. Synthesis & Recommendations (policy + investment)
10. Appendix (key debate quotes, source list)

Use markdown throughout: headers, tables, bold, bullet points. Make it publication-ready.""",
    tools=[{
        "type": "agent_toolset_20260401",
        "default_config": {"enabled": True},
    }],
)
print(f"  SYNTHESIZER_AGENT_ID = {synthesizer.id}")


# ── Save all IDs ──────────────────────────────────────────
set_key(ENV_FILE, "ENV_ID_AGI",            env.id)
set_key(ENV_FILE, "RESEARCHER_AGENT_ID",   researcher.id)
set_key(ENV_FILE, "BLUE_TEAM_AGENT_ID",    blue_team.id)
set_key(ENV_FILE, "RED_TEAM_AGENT_ID",     red_team.id)
set_key(ENV_FILE, "SYNTHESIZER_AGENT_ID",  synthesizer.id)

print(f"""
✅ All 4 agents created. IDs saved to {ENV_FILE}

Next step:
  python agi_debate/orchestrate.py
""")
