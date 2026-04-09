"""
AGI Economic Impact — Research + Red/Blue Team Debate
Multi-agent orchestration using Claude Managed Agents

Flow:
  Phase 1  Research          1 session  (Researcher: 20+ web searches)
  Phase 2  Opening Arguments 2 parallel (Blue + Red round 1)
  Phase 3  Rebuttals         2 parallel (Blue + Red round 2)
  Phase 4  Closing           2 parallel (Blue + Red round 3)
  Phase 5  Synthesis         1 session  (writes agi_impact_report.md)
  Phase 6  Push to GitHub

Usage:
  python agi_debate/orchestrate.py
"""
import os
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from pathlib import Path

from dotenv import load_dotenv

# Allow running from repo root or agi_debate/
sys.path.insert(0, str(Path(__file__).parent.parent))
from agi_debate.utils import run_session, download_session_files

load_dotenv()

ENV_ID      = os.environ["ENV_ID_AGI"]
AGENTS      = {
    "researcher":  os.environ["RESEARCHER_AGENT_ID"],
    "blue":        os.environ["BLUE_TEAM_AGENT_ID"],
    "red":         os.environ["RED_TEAM_AGENT_ID"],
    "synthesizer": os.environ["SYNTHESIZER_AGENT_ID"],
}
GITHUB_REPO = os.environ.get("GITHUB_REPO", "josecookai/research-agent")

RUN_DATE    = datetime.now().strftime("%Y-%m-%d")
REPORT_DIR  = Path(__file__).parent.parent / "reports" / f"agi-debate-{RUN_DATE}"
REPORT_DIR.mkdir(parents=True, exist_ok=True)
REPO_ROOT   = Path(__file__).parent.parent


# ── Helpers ──────────────────────────────────────────────

def save(filename: str, content: str) -> Path:
    path = REPORT_DIR / filename
    path.write_text(content, encoding="utf-8")
    return path


def banner(title: str):
    bar = "═" * 60
    print(f"\n{bar}")
    print(f"  {title}")
    print(f"{bar}")


def parallel_debate(
    round_label: str,
    blue_prompt: str,
    red_prompt: str,
    blue_file: str,
    red_file: str,
) -> tuple[str, str]:
    """Run Blue + Red sessions in parallel, save outputs, return texts."""
    banner(f"Debate: {round_label}")

    def _run(side: str, agent_id: str, prompt: str, title: str):
        _, text = run_session(
            agent_id=agent_id,
            env_id=ENV_ID,
            message=prompt,
            label=side,
            title=title,
        )
        return side, text

    results: dict[str, str] = {}
    with ThreadPoolExecutor(max_workers=2) as ex:
        futures = {
            ex.submit(_run, "BLUE", AGENTS["blue"], blue_prompt, f"Blue — {round_label}"): "blue",
            ex.submit(_run, "RED",  AGENTS["red"],  red_prompt,  f"Red  — {round_label}"): "red",
        }
        for fut in as_completed(futures):
            side, text = fut.result()
            results[side.lower()] = text
            print(f"\n  {side} done: {len(text):,} chars")

    save(blue_file, f"# Blue Team: {round_label}\n\n{results['blue']}")
    save(red_file,  f"# Red Team: {round_label}\n\n{results['red']}")
    return results["blue"], results["red"]


# ── Phase 1: Research ────────────────────────────────────

def phase_research() -> str:
    banner("Phase 1 — Deep Research")

    prompt = """Conduct comprehensive research on AGI's economic impact. Search at least 20 times.

Cover ALL of the following with specific data, statistics, and source URLs:

═══ UNEMPLOYMENT ═══
• Historical automation waves: Industrial Revolution (1760-1840), agricultural mechanization,
  computerization (1980s-2000s) — net job creation or destruction data
• Current projections: Oxford "47% of US jobs at risk" (Frey & Osborne 2013),
  WEF Future of Jobs Report 2025, McKinsey Global Institute automation studies
• Job categories most/least vulnerable (cognitive routine vs. non-routine)
• Speed of displacement historically vs. adaptation/retraining timelines

═══ GDP IMPACT ═══
• Goldman Sachs: AI could add 7% to global GDP — find the full report data
• Productivity gains from automation historically (electricity, computers)
• Capital vs. labor income share trends (FRED data, Piketty research)
• IMF projections on AI and economic growth
• Country-level differences (US, China, EU, Global South)

═══ SOCIAL STABILITY ═══
• Luddite movement (1811-1816): causes, timeline, outcomes
• Great Depression unemployment → political extremism (Germany, US, Europe)
• US deindustrialization (1970s-2000s): rust belt → political polarization data
• Research on inequality → unrest threshold (Gini coefficient correlations)
• UBI experiments and proposals (Finland, Kenya, Stockton CA)

═══ US STOCK MARKET ═══
• AI stock premium today: Nvidia, Microsoft, Google valuations and growth
• Historical market impact of technology revolutions (dot-com, mobile, cloud)
• P/E ratios and market concentration in AI era
• Sectors trading at premium vs. discount due to AI fears

═══ AGI TIMELINES ═══
• Expert surveys on AGI arrival (Metaculus, AI Impacts, Epoch AI)
• Yoshua Bengio, Geoffrey Hinton, Sam Altman, Dario Amodei public statements
• Current frontier model capabilities vs. AGI benchmarks

Output a structured research brief with numbered sections, key data points, expert quotes, and full source URLs."""

    _, text = run_session(
        agent_id=AGENTS["researcher"],
        env_id=ENV_ID,
        message=prompt,
        label="RESEARCHER",
        title="AGI Research Brief",
    )
    save("00_research_brief.md", f"# AGI Impact — Research Brief\n\nGenerated: {RUN_DATE}\n\n{text}")
    print(f"\n  Research brief: {len(text):,} chars")
    return text


# ── Phase 2: Opening Arguments ───────────────────────────

def phase_opening(research: str) -> tuple[str, str]:
    research_excerpt = research[:9000]

    blue_prompt = f"""## Research Brief (use this as your evidence base)
{research_excerpt}

## Your Task: Opening Argument — Blue Team (Optimist)

Make a comprehensive, data-driven opening argument that AGI's net economic impact will be POSITIVE.
Address each topic with specific evidence, historical analogies, and probability estimates:

**1. Unemployment** — Why net job creation outpaces destruction
- Cite specific historical examples (Industrial Revolution, computing era)
- Quantify: which % of jobs are at risk vs. how many new categories emerge
- Timeline: transition pain is real but temporary

**2. GDP Growth** — Mechanism and distribution
- Quantify the productivity gain (cite Goldman Sachs or comparable study)
- Explain how gains reach ordinary workers (not just capital owners)
- Compare to historical precedents (electricity: +40% productivity 1890-1930)

**3. Social Stability** — Why this transition will be manageable
- Contrast with historical unrest cases (what was different then)
- Role of social safety nets, retraining programs, UBI pilots
- Democratic institutions resilience

**4. US Stock Market & Winners**
- Top 10 specific companies most likely to benefit (name, sector, mechanism)
- Market structure under AGI scenario (concentration vs. broad gains)
- Estimated upside ranges

**5. Pre-empt Red Team's Strongest Arguments**
- Acknowledge their 3 best points, then rebut each with evidence

Format with clear headers. Be specific, cite data from the research brief."""

    red_prompt = f"""## Research Brief (use this as your evidence base)
{research_excerpt}

## Your Task: Opening Argument — Red Team (Pessimist)

Make a comprehensive, data-driven opening argument that AGI's net economic impact will be NEGATIVE / HIGHLY DISRUPTIVE.
Address each topic with specific evidence, historical analogies, and probability estimates:

**1. Unemployment** — Why AGI is qualitatively different from past automation
- Cognitive automation: first time white-collar, creative, and knowledge work is disrupted simultaneously
- Speed differential: AI adoption 10x faster than electrification or computerization
- Quantify: Oxford study 47%, Goldman Sachs 300M jobs, McKinsey 30% by 2030
- Structural (not cyclical): new jobs require skills displaced workers cannot retrain into

**2. GDP Concentration** — Why gains don't reach workers
- Capital vs. labor income share data (cite Piketty / FRED data from research)
- Winner-take-all dynamics: superstar firms, superstar workers
- Historical precedent: deindustrialization GDP grew but wages stagnated for 30 years
- Gini coefficient trajectory under automation

**3. Social Instability & Unrest** — Historical precedents are alarming
- Luddites: specific mechanisms (speed + concentration + no safety net)
- Great Depression: unemployment → fascism in Germany, populism globally
- 2010s tech disruption: already seeing political backlash (Brexit, MAGA, Le Pen)
- Threshold analysis: at what unemployment rate does democratic stability break?

**4. US Stock Market & Losers**
- Top 10 specific companies most at risk (name, sector, mechanism)
- Market bubble risk: current AI valuations unsustainable
- Sector concentration creates systemic fragility

**5. Pre-empt Blue Team's Strongest Arguments**
- Acknowledge their 3 best points, then rebut each with evidence

Format with clear headers. Be specific, cite data from the research brief."""

    return parallel_debate(
        round_label="Round 1 — Opening Arguments",
        blue_prompt=blue_prompt,
        red_prompt=red_prompt,
        blue_file="01_blue_opening.md",
        red_file="01_red_opening.md",
    )


# ── Phase 3: Rebuttals ───────────────────────────────────

def phase_rebuttals(research: str, blue_r1: str, red_r1: str) -> tuple[str, str]:
    r = research[:4000]
    b1 = blue_r1[:5000]
    r1 = red_r1[:5000]

    blue_prompt = f"""## Context
Research Brief (excerpt): {r}

## Red Team's Opening Argument (what you must rebut):
{r1}

## Your Previous Opening Argument:
{b1}

## Your Task: Rebuttal — Blue Team

1. **Identify Red Team's 3 Strongest Arguments** — quote them directly
2. **Systematic Rebuttal** — for each argument:
   - Acknowledge what's valid (steel-man)
   - Provide counter-evidence with data
   - Explain why their historical analogies are flawed or incomplete
3. **Deepen Your Case** — add new evidence you didn't use in Round 1:
   - Search for additional data points if needed
   - Address the structural unemployment argument specifically
   - Counter the Gini/inequality argument with evidence
4. **Force Red Team to Defend** — pose 3 specific questions they must answer in Round 3

Be analytically sharp. Show you understand the strongest version of their argument."""

    red_prompt = f"""## Context
Research Brief (excerpt): {r}

## Blue Team's Opening Argument (what you must rebut):
{b1}

## Your Previous Opening Argument:
{r1}

## Your Task: Rebuttal — Red Team

1. **Identify Blue Team's 3 Strongest Arguments** — quote them directly
2. **Systematic Rebuttal** — for each argument:
   - Acknowledge what's valid (steel-man)
   - Provide counter-evidence with data
   - Explain why their historical analogies fail for AGI specifically
3. **Deepen Your Case** — add new evidence you didn't use in Round 1:
   - Search for additional data points if needed
   - Address the "new jobs will emerge" argument directly with data
   - Counter the "safety nets will cushion" argument with evidence
4. **Force Blue Team to Defend** — pose 3 specific questions they must answer in Round 3

Be analytically sharp. Show you understand the strongest version of their argument."""

    return parallel_debate(
        round_label="Round 2 — Rebuttals",
        blue_prompt=blue_prompt,
        red_prompt=red_prompt,
        blue_file="02_blue_rebuttal.md",
        red_file="02_red_rebuttal.md",
    )


# ── Phase 4: Cross-examination & Closing ─────────────────

def phase_closing(
    blue_r1: str, red_r1: str,
    blue_r2: str, red_r2: str,
) -> tuple[str, str]:

    debate_so_far_blue = f"""
Blue Opening:   {blue_r1[:2500]}
Red Opening:    {red_r1[:2500]}
Blue Rebuttal:  {blue_r2[:2000]}
Red Rebuttal:   {red_r2[:2000]}
"""
    debate_so_far_red = debate_so_far_blue  # same context for both

    blue_prompt = f"""## Full Debate So Far:
{debate_so_far_blue}

## Your Task: Cross-examination & Closing Statement — Blue Team

**Part 1: Cross-examination (answer Red Team's questions, ask your own)**
- Answer the 3 questions Red Team posed in Round 2
- Ask Red Team 3 penetrating questions that expose weaknesses in their pessimist case
  (focus on: what specific historical case is truly analogous to AGI? What would falsify their thesis?)

**Part 2: Closing Statement**
Structure your closing as:
1. **What this debate proved**: 2 points where you moved the argument forward
2. **Core disagreement**: What is the fundamental assumption difference between teams?
3. **Probability estimates** (be specific):
   - Unemployment rate in 10 years: ___% (range)
   - GDP growth per decade under AGI: ___%
   - Probability of major social unrest (>1930s scale): ___%
   - S&P 500 in 10 years: bullish / bearish case with numbers
4. **The single most important argument** for the optimist case (one paragraph, maximum impact)
5. **What you concede** to the Red Team (intellectual honesty)"""

    red_prompt = f"""## Full Debate So Far:
{debate_so_far_red}

## Your Task: Cross-examination & Closing Statement — Red Team

**Part 1: Cross-examination (answer Blue Team's questions, ask your own)**
- Answer the 3 questions Blue Team posed in Round 2
- Ask Blue Team 3 penetrating questions that expose weaknesses in their optimist case
  (focus on: what specific evidence shows new jobs will match displaced workers' skills? What's the retraining timeline?)

**Part 2: Closing Statement**
Structure your closing as:
1. **What this debate proved**: 2 points where you moved the argument forward
2. **Core disagreement**: What is the fundamental assumption difference between teams?
3. **Probability estimates** (be specific):
   - Unemployment rate in 10 years: ___% (range)
   - GDP growth per decade under AGI: ___%
   - Probability of major social unrest (>1930s scale): ___%
   - S&P 500 in 10 years: bullish / bearish case with numbers
4. **The single most important argument** for the pessimist case (one paragraph, maximum impact)
5. **What you concede** to the Blue Team (intellectual honesty)"""

    return parallel_debate(
        round_label="Round 3 — Cross-exam & Closing",
        blue_prompt=blue_prompt,
        red_prompt=red_prompt,
        blue_file="03_blue_closing.md",
        red_file="03_red_closing.md",
    )


# ── Phase 5: Synthesis ───────────────────────────────────

def phase_synthesis(research: str, blue: dict, red: dict) -> None:
    banner("Phase 5 — Final Synthesis Report")

    prompt = f"""## Research Brief
{research[:5000]}

## Debate Transcript Summary

### BLUE TEAM (Optimist)
Opening:  {blue['r1'][:2500]}
Rebuttal: {blue['r2'][:2000]}
Closing:  {blue['r3'][:1500]}

### RED TEAM (Pessimist)
Opening:  {red['r1'][:2500]}
Rebuttal: {red['r2'][:2000]}
Closing:  {red['r3'][:1500]}

---

## Your Task: Write the Definitive Report

Save to: /mnt/session/outputs/agi_impact_report.md

Use this EXACT structure:

# AGI Economic Impact: A Comprehensive Analysis
## Research + Red Team / Blue Team Debate — {RUN_DATE}

### Executive Summary
[3 scenarios with assigned probabilities. Key investment implications. ~500 words.]

### Methodology
[Research approach, debate structure, agent roles, limitations]

### Part I: Research Findings
[Key data points, statistics, timeline estimates — all cited]

### Part II: The Debate

#### Topic Comparison Table
| Topic | Blue Team (Optimist) | Red Team (Pessimist) |
|-------|---------------------|----------------------|
| Unemployment | ... | ... |
| GDP | ... | ... |
| Social Stability | ... | ... |
| US Stocks | ... | ... |
| Historical Analogy | ... | ... |

[For each topic: summarize both positions, identify core disagreement, assess evidence quality]

### Part III: Unemployment Analysis

#### Scenario A — Optimistic (probability: X%)
- Timeline, % displaced, new jobs created, recovery period

#### Scenario B — Base Case (probability: X%)
- Timeline, % displaced, safety net requirements, partial recovery

#### Scenario C — Pessimistic (probability: X%)
- Timeline, % displaced, structural unemployment, political consequences

### Part IV: GDP Impact
- 10-year projections by scenario (table)
- Capital vs. labor income share trajectory
- Country-level divergence (US vs. EU vs. China vs. Global South)
- Gini coefficient projections

### Part V: Social Stability & Unrest Risk

#### Historical Risk Matrix
| Historical Event | Unemployment % | GDP Change | Outcome | Similarity to AGI Scenario |
|-----------------|----------------|------------|---------|---------------------------|
| Luddite movement | ... | ... | ... | ... |
| Great Depression | ... | ... | ... | ... |
| Deindustrialization | ... | ... | ... | ... |

- Current risk factors vs. stabilizers
- Geographic hotspots (most vulnerable countries/regions)
- Trigger threshold analysis

### Part VI: US Stock Market Analysis

#### Macro Assessment
[Bull case, bear case, base case for S&P 500 over 10 years]

#### Top 10 Beneficiary Companies
| Company | Sector | Investment Thesis | Estimated Upside | Key Risk |
|---------|--------|------------------|-----------------|----------|
| ... | ... | ... | ...% | ... |

#### Top 10 At-Risk Companies
| Company | Sector | Disruption Thesis | Estimated Downside | Mitigation Path |
|---------|--------|------------------|-------------------|-----------------|
| ... | ... | ... | ...% | ... |

#### Sector Rotation Framework
[Which sectors to overweight / underweight across scenarios]

### Part VII: Synthesis & Recommendations

#### Where Blue and Red Teams Agree
[3-5 points of genuine consensus]

#### Core Unresolved Disagreements
[The 3 key empirical questions that determine which scenario plays out]

#### Policy Recommendations
1. [for governments]
2. [for central banks]
3. [for education systems]
4. [for social safety nets]
5. [for international coordination]

#### Investment Principles for the AGI Transition
1-5 actionable principles with conviction

#### Key Milestones to Monitor
[Events/metrics that would confirm optimistic vs. pessimistic scenario]

### Appendix
- Strongest Blue Team quotes
- Strongest Red Team quotes
- Full source list from research
- Probability summary table

---

Write at publication quality. Use all markdown features. Minimum 4,000 words."""

    sess_id, text = run_session(
        agent_id=AGENTS["synthesizer"],
        env_id=ENV_ID,
        message=prompt,
        label="SYNTHESIZER",
        title="AGI Synthesis Report",
    )

    # Try to download the file the synthesizer wrote
    files = download_session_files(sess_id, str(REPORT_DIR))
    if not files:
        # Fallback: save the streamed text
        fallback = save("agi_impact_report.md", text)
        print(f"  📄 Saved fallback: {fallback}")

    # Always create the index file
    _write_index()


def _write_index():
    """Create a README.md index for the report directory."""
    files = sorted(REPORT_DIR.glob("*.md"))
    links = "\n".join(f"- [{f.name}]({f.name})" for f in files)
    index = f"""# AGI Economic Impact — Debate Report

**Date:** {RUN_DATE}
**Method:** Claude Managed Agents — Research + Red/Blue Team Debate

## Files

{links}

## Structure

| Phase | File | Description |
|-------|------|-------------|
| Research | `00_research_brief.md` | Deep web research (20+ searches) |
| Debate R1 | `01_blue_opening.md` / `01_red_opening.md` | Opening arguments |
| Debate R2 | `02_blue_rebuttal.md` / `02_red_rebuttal.md` | Rebuttals |
| Debate R3 | `03_blue_closing.md` / `03_red_closing.md` | Cross-exam & closing |
| Synthesis | `agi_impact_report.md` | Final comprehensive report |

## Agents

- **Researcher** — 20+ web searches across economic literature
- **Blue Team** — Optimist: net positive AGI outcomes
- **Red Team** — Pessimist: disruptive/negative AGI outcomes
- **Synthesizer** — Balanced final analysis
"""
    save("README.md", index)


# ── Phase 6: Push to GitHub ───────────────────────────────

def phase_push():
    banner("Phase 6 — Push to GitHub")

    # Ensure reports/ is not gitignored
    gitignore = REPO_ROOT / ".gitignore"
    gi_text = gitignore.read_text()
    if "reports/" in gi_text:
        gitignore.write_text(gi_text.replace("reports/\n", ""))
        print("  📝 Removed reports/ from .gitignore")

    report_rel = f"reports/agi-debate-{RUN_DATE}/"
    cmds = [
        ["git", "-C", str(REPO_ROOT), "add", report_rel],
        ["git", "-C", str(REPO_ROOT), "add", "agi_debate/"],
        ["git", "-C", str(REPO_ROOT), "add", ".gitignore"],
        ["git", "-C", str(REPO_ROOT), "commit", "-m",
         f"research: AGI economic impact red/blue team debate {RUN_DATE}"],
        ["git", "-C", str(REPO_ROOT), "push"],
    ]

    for cmd in cmds:
        result = subprocess.run(cmd, capture_output=True, text=True)
        label = " ".join(cmd[3:])
        if result.returncode == 0:
            out = result.stdout.strip()
            print(f"  ✅ {label}" + (f" — {out}" if out else ""))
        else:
            err = (result.stderr or result.stdout).strip()[:120]
            print(f"  ⚠️  {label}: {err}")

    print(f"\n🔗 https://github.com/{GITHUB_REPO}/tree/main/{report_rel}")


# ── Main ─────────────────────────────────────────────────

def main():
    t0 = time.time()
    print(f"""
╔══════════════════════════════════════════════════════════╗
║   AGI Economic Impact — Research + Red/Blue Team Debate  ║
║   {RUN_DATE}                                             ║
║   Output: reports/agi-debate-{RUN_DATE}/               ║
╚══════════════════════════════════════════════════════════╝""")

    # Phase 1
    research = phase_research()

    # Phase 2 — Opening
    blue_r1, red_r1 = phase_opening(research)

    # Phase 3 — Rebuttals
    blue_r2, red_r2 = phase_rebuttals(research, blue_r1, red_r1)

    # Phase 4 — Closing
    blue_r3, red_r3 = phase_closing(blue_r1, red_r1, blue_r2, red_r2)

    # Phase 5 — Synthesis
    phase_synthesis(
        research,
        blue={"r1": blue_r1, "r2": blue_r2, "r3": blue_r3},
        red={"r1": red_r1,  "r2": red_r2,  "r3": red_r3},
    )

    # Phase 6 — Push
    phase_push()

    elapsed = time.time() - t0
    print(f"\n✅ Complete in {elapsed/60:.1f} min")
    print(f"📁 {REPORT_DIR}")


if __name__ == "__main__":
    main()
