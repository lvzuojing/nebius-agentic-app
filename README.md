# 🤖 Nebius Agentic Research — multi-agent research assistant

> **Nebius × NVIDIA Global AI Hackathon 2026** submission (Agentic Apps /
> Best Apps and Agents track). An agentic app built on **open infrastructure**:
> NVIDIA open models served through **Nebius** AI compute.

A topic goes through a multi-agent pipeline:

```
        ┌─────────┐
topic → │ Planner │  decomposes into 3 sub-questions
        └────┬────┘
   ┌─────────┼──────────┐
   ▼         ▼          ▼
 ┌────────┐ ┌────────┐ ┌────────┐   Researcher = ReAct loop:
 │Research│ │Research│ │Research│   LLM → tool call → result → … → answer
 │ er #1  │ │ er #2  │ │ er #3  │   tools: web_search · fetch_url · calculator
 └───┬────┘ └───┬────┘ └───┬────┘
     └──────────┼──────────┘
                ▼
        ┌─────────┐
        │ Writer  │  assembles a cited brief
        └─────────┘
```

This mirrors the winning pattern from 2026 agentic hackathons: **multi-agent
orchestration beats a single clever prompt** — decompose the problem into roles
with narrow contracts, give each agent tool access, and put a writer on top.

---

## ✨ Why it fits the hackathon

| Hackathon requirement | How this repo satisfies it |
|---|---|
| Build with **NVIDIA open models** | Researcher/Writer call an NVIDIA model (`nvidia/llama-3.1-70b-instruct`) |
| on **NVIDIA open infrastructure** | Served via the **Nebius** OpenAI-compatible endpoint |
| **Agentic** application | Planner → multi-Researcher ReAct loops → Writer |
| Solo-friendly | No team required; one `python app.py` |
| Runnable now | **Offline mock mode** needs no API key; real mode with one env var |

---

## 🚀 Quick start

```bash
pip install -r requirements.txt

# offline demo (no key) — multi-agent loop fully visible
python app.py                 # web UI on http://127.0.0.1:8090
# or CLI:
python agent.py "Should small teams adopt an agentic architecture?" --mock

# real mode: NVIDIA model via Nebius (needs a Nebius API key)
export NEBIUS_API_KEY=...
python agent.py "your topic" --model nvidia/llama-3.1-70b-instruct
python app.py                 # flips to real mode automatically
```

`tools.py` currently returns clearly-labelled offline stubs for
`web_search` / `fetch_url` so the demo never breaks on a missing key; swap in a
real search/fetch backend in the `live=True` branch to go fully live.

---

## 🎬 Demo video script (≤ 3 min, English)

1. **(0:00–0:25)** Open `app.py` → `http://127.0.0.1:8090`. Explain the
   problem: researching a topic by hand is slow; an agentic pipeline is faster.
2. **(0:25–1:10)** Show the architecture (Planner → 3 Researchers → Writer).
   Click "研究" with a topic. Watch the step stream: plan, each researcher's
   tool call + answer, then the assembled brief.
3. **(1:10–2:00)** Open `agent.py`. Point at `TOOLS_SPEC` (web_search,
   fetch_url, calculator) and the ReAct `run_agent` loop. Note each Researcher
   is an independent tool-calling agent.
4. **(2:00–2:40)** Show how it goes real: `export NEBIUS_API_KEY=...` and the
   `NebiusLLM` class (OpenAI-compatible → Nebius → NVIDIA model). Emphasise
   "open infrastructure, open models."
5. **(2:40–3:00)** Close: "Multi-agent orchestration, NVIDIA models, Nebius
   compute — built in ~one file."

---

## 📦 Files

```
agent.py      # multi-agent orchestration + LLM backends (Mock / Nebius)
tools.py      # web_search, fetch_url, calculator (offline-safe)
app.py        # web UI that streams the agent steps
index.html    # UI markup
requirements.txt
LICENSE       # MIT
```

## 📝 License

MIT — see [LICENSE](LICENSE).
