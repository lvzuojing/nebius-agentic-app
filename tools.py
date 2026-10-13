#!/usr/bin/env python3
"""Tool implementations for the Nebius agentic research app.

Two of the three tools have an offline "mock" path so the whole multi-agent
loop can be demonstrated without a Nebius API key. In real mode the tool
results come from live sources (a real search/fetch would plug in here).
"""
import re


def web_search(query, live=False):
    if live:
        # Placeholder for a real search backend (SerpAPI / Bing / Brave).
        # Kept offline-safe: returns a clearly-labelled stub so the demo
        # never fails on a missing key.
        return f"[live search not configured] query={query!r}"
    return (
        f"Web results for {query!r}:\n"
        f"1. {query} — overview: a fast-moving area in 2026 with several "
        f"open-source efforts.\n"
        f"2. Key trend: open infrastructure (NVIDIA models + Nebius compute) "
        f"is lowering the barrier to agentic apps.\n"
        f"3. Adoption is accelerating across finance, health, and dev tools.\n"
        f"4. Reference: example.com/{query.lower().replace(' ', '-')}"
    )


def fetch_url(url, live=False):
    if live:
        return f"[live fetch not configured] url={url!r}"
    return f"Content of {url}: placeholder paragraph summarising the topic."


def calculator(expr):
    allowed = set("0123456789+-*/(). %")
    if set(expr) - allowed:
        return "error: only arithmetic expressions are supported"
    try:
        result = eval(expr, {"__builtins__": {}}, {})  # noqa: S307 (sandboxed)
        return f"{expr} = {result}"
    except Exception as e:  # noqa: BLE001
        return f"error: {e}"
