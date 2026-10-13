# Devpost Submission — Nebius × NVIDIA Global AI Hackathon 2026

> Copy the sections below into the Devpost entry form. Replace the
> `DEMO_VIDEO_URL` placeholder with your uploaded video link. For the **live**
> demo, set `NEBIUS_API_KEY` so the app uses a real NVIDIA model; without it the
> app runs identically in offline mock mode.

---

**Project name:** Nebius Agentic Research — multi-agent research assistant

**Tagline (one line):** A topic flows through a Planner → multi-Researcher
(ReAct tool-calling) → Writer pipeline, powered by **NVIDIA open models on
Nebius** infrastructure.

**Demo video URL:** `DEMO_VIDEO_URL`

**Built with:** Python · NVIDIA open models (served via **Nebius** OpenAI-
compatible endpoint) · multi-agent orchestration · Streamable-style tool loop

---

## Story

### Inspiration
The winning pattern in 2026 agentic hackathons is **multi-agent orchestration,
not one clever prompt** — decompose the problem into roles with narrow
contracts, give each agent tool access, and put a writer on top. I built exactly
that, on open infrastructure.

### What it does
A research topic is decomposed by a **Planner** into three sub-questions. Each is
handled by an independent **Researcher** agent running a ReAct loop (LLM → tool
call → result → … → answer) over `web_search` / `fetch_url` / `calculator`.
A **Writer** assembles the sourced brief.

### How we built it
- `agent.py` — the orchestration: `plan_subquestions` → N×`run_agent` (ReAct) →
  `write_report`, plus two LLM backends:
  - `MockLLM` — scripted, **runs with no API key** (offline demo of the
    architecture).
  - `NebiusLLM` — OpenAI-compatible client pointed at Nebius, serving an NVIDIA
    model (`nvidia/llama-3.1-70b-instruct`).
- `tools.py` — tools with offline-safe stubs; the `live=True` branch is where a
  real search/fetch backend plugs in.
- `app.py` + `index.html` — a web UI that **streams every agent step** so the
  orchestration is visible in a demo.

### Challenges we ran into
Keeping the agent loop provider-agnostic: the same tool-calling contract works
for both the offline mock and a real NVIDIA model on Nebius, so the demo never
depends on a key being present.

### Accomplishments we're proud of
A genuinely agentic app on **open models + open infrastructure** that is
reproducible by anyone with a `pip install` and (optionally) a Nebius key.

### What's next
Swap the stub tools for live search/fetch, add a critic agent for citation
checking, and benchmark NVIDIA model choices on Nebius.

### What we learned
Open infrastructure (NVIDIA models + Nebius compute) makes multi-agent apps
practical for solo builders in 2026.

---

## Judging criteria mapping
- **Coding / Agentic Engineering:** real multi-agent orchestration with a
  provider-agnostic tool-calling loop.
- **Best Apps and Agents:** a usable research assistant, not a toy prompt.
- **Open infrastructure:** NVIDIA open models served through Nebius; MIT-licensed.
- **Reproducibility:** offline mock mode + one-command real mode.
