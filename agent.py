#!/usr/bin/env python3
"""Multi-agent research app — the Nebius x NVIDIA hackathon entry.

Orchestration:
    Planner  -> splits a topic into sub-questions
    Researcher (xN, each uses an NVIDIA open model via Nebius) -> ReAct loop
    Writer   -> assembles a cited brief

Two LLM backends:
    MockLLM    : scripted, runs with NO API key (offline demo)
    NebiusLLM  : OpenAI-compatible client -> Nebius endpoint -> NVIDIA model

Run:
    python agent.py "Should I use an agentic architecture for X?"
    python agent.py "..." --mock            # force offline mock
    NEBIUS_API_KEY=... python agent.py "..." --model nvidia/llama-3.1-70b-instruct
"""
import argparse
import json
import os
import re
import sys

from tools import web_search, fetch_url, calculator

TOOLS_SPEC = [
    {
        "type": "function",
        "function": {
            "name": "web_search",
            "description": "Search the web for a short query and return snippets.",
            "parameters": {
                "type": "object",
                "properties": {"query": {"type": "string"}},
                "required": ["query"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "fetch_url",
            "description": "Fetch the text content of a URL.",
            "parameters": {
                "type": "object",
                "properties": {"url": {"type": "string"}},
                "required": ["url"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "calculator",
            "description": "Evaluate a basic arithmetic expression, e.g. '2*3+1'.",
            "parameters": {
                "type": "object",
                "properties": {"expr": {"type": "string"}},
                "required": ["expr"],
            },
        },
    },
]

TOOL_FUNCS = {"web_search": web_search, "fetch_url": fetch_url, "calculator": calculator}


# ---------------------------------------------------------------------------
# LLM backends
# ---------------------------------------------------------------------------
class MockLLM:
    """Offline scripted LLM so the whole loop is demonstrable without a key.

    Behaviour: on the first turn (no tool result yet) it issues a web_search;
    once a tool result has been fed back it returns a grounded final answer.
    """

    def chat_with_tools(self, system, messages, max_steps=4):
        """Returns either a tool_call dict or a final 'answer' string."""
        last_user = ""
        for m in reversed(messages):
            if m["role"] == "user":
                last_user = m["content"]
                break
        # After a tool result is in context, produce the final answer.
        if messages and messages[-1].get("role") == "tool":
            return {"answer": (
                f"Based on gathered sources, '{last_user}' can be summarised as: "
                f"open infrastructure (NVIDIA open models + Nebius compute) makes "
                f"agentic apps practical in 2026; the main trade-off is "
                f"orchestration overhead versus a single-prompt solution."
            )}
        # First turn: ground the answer with a search.
        return {"tool": "web_search", "args": {"query": last_user.strip()}}


class NebiusLLM:
    """OpenAI-compatible client pointed at Nebius, serving an NVIDIA model."""

    def __init__(self, model, api_key=None, base_url="https://api.nebius.com/v1"):
        from openai import OpenAI  # lazy import; only needed in real mode
        self.model = model
        self.client = OpenAI(api_key=api_key or os.environ["NEBIUS_API_KEY"],
                             base_url=base_url)

    def chat_with_tools(self, system, messages, max_steps=4):
        resp = self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "system", "content": system}] + messages,
            tools=TOOLS_SPEC,
            tool_choice="auto",
        )
        msg = resp.choices[0].message
        if msg.tool_calls:
            tc = msg.tool_calls[0]
            return {"tool": tc.function.name,
                    "args": json.loads(tc.function.arguments or "{}")}
        return {"answer": msg.content or ""}


# ---------------------------------------------------------------------------
# Agent loop (ReAct)
# ---------------------------------------------------------------------------
def run_agent(sub_question, llm, steps, live=False, max_steps=5):
    system = ("You are a meticulous researcher. Use the provided tools to find "
              "facts, then give a concise, sourced answer. When done, reply with "
              "a final answer (no tool call).")
    messages = [{"role": "user", "content": sub_question}]
    for _ in range(max_steps):
        decision = llm.chat_with_tools(system, messages)
        if "answer" in decision:
            steps.append({"role": "answer", "text": decision["answer"]})
            return decision["answer"]
        tool = decision["tool"]
        args = decision["args"]
        result = TOOL_FUNCS[tool](live=live, **args)
        steps.append({"role": "tool", "tool": tool, "args": args,
                      "result": str(result)[:600]})
        messages.append({"role": "assistant", "content": "",
                         "tool_calls": [{"function": {"name": tool,
                                                      "arguments": json.dumps(args)}}]})
        messages.append({"role": "tool", "name": tool, "content": str(result)})
    return "(no final answer produced)"


def plan_subquestions(topic, llm, steps):
    if isinstance(llm, MockLLM):
        t = topic.rstrip("?!. ？！。")
        parts = [f"What is the current state of {t}?",
                 f"What are the trade-offs of {t}?",
                 f"How should a team adopt {t}?"]
        steps.append({"role": "plan", "text": " · ".join(parts)})
        return parts
    # real mode: ask the model to decompose
    r = run_agent(
        f"Decompose this research topic into exactly 3 sub-questions, one per "
        f"line, no numbering preamble: {topic}", llm, steps)
    return [l.strip("0123456789. ") for l in r.splitlines() if l.strip()][:3]


def write_report(topic, sub_answers, llm, steps):
    joined = "\n\n".join(f"### {i+1}. {a}" for i, a in enumerate(sub_answers))
    if isinstance(llm, MockLLM):
        report = (f"# Research brief: {topic}\n\n"
                  f"_Generated by the Nebius Agentic Research multi-agent "
                  f"(Planner → Researchers → Writer), using NVIDIA open models "
                  f"on Nebius infrastructure._\n\n"
                  f"{joined}\n\n"
                  f"## Bottom line\nOpen infrastructure makes agentic apps "
                  f"practical; start with one narrow agent, add orchestration "
                  f"only where the task genuinely decomposes.")
        steps.append({"role": "write", "text": "assembled brief (mock)"})
        return report
    return run_agent(f"Write a tight research brief on '{topic}' from:\n{joined}",
                     llm, steps)


def run_research(topic, llm, live=False):
    steps = []
    subs = plan_subquestions(topic, llm, steps)
    answers = []
    for i, sq in enumerate(subs, 1):
        steps.append({"role": "sub", "text": f"Researcher #{i}: {sq}"})
        answers.append(run_agent(sq, llm, steps, live=live))
    report = write_report(topic, answers, llm, steps)
    return report, steps


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("topic", help="research topic / question")
    ap.add_argument("--mock", action="store_true", help="force offline mock LLM")
    ap.add_argument("--model", default="nvidia/llama-3.1-70b-instruct")
    args = ap.parse_args()

    if args.mock or not os.environ.get("NEBIUS_API_KEY"):
        if not args.mock:
            print("[info] NEBIUS_API_KEY not set -> using offline MockLLM.",
                  file=sys.stderr)
        llm = MockLLM()
    else:
        llm = NebiusLLM(args.model)

    report, steps = run_research(args.topic, llm)
    print("\n".join(f"[{s['role']}] {s.get('text', s.get('tool',''))}"
                     for s in steps))
    print("\n" + "=" * 60 + "\n")
    print(report)


if __name__ == "__main__":
    main()
