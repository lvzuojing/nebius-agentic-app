#!/usr/bin/env python3
"""Minimal web UI for the Nebius Agentic Research app (stdlib only).

Runs the multi-agent research loop and streams each step (plan / researcher /
tool call / answer / write) into the browser, so the agentic orchestration is
visible in a demo video without a terminal.

    python app.py                       # mock mode (no key)
    NEBIUS_API_KEY=... python app.py    # real NVIDIA model via Nebius
"""
import json
import os
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

from agent import run_research, MockLLM, NebiusLLM  # noqa: E402


class Handler(BaseHTTPRequestHandler):
    def _send(self, code, body, ctype="application/json; charset=utf-8"):
        data = body.encode("utf-8") if isinstance(body, str) else body
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(data)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self):
        if self.path in ("/", "/index.html"):
            with open(os.path.join(os.path.dirname(__file__),
                                   "index.html"), encoding="utf-8") as f:
                self._send(200, f.read(), "text/html; charset=utf-8")
        else:
            self._send(404, "not found")

    def do_POST(self):
        if self.path != "/research":
            self._send(404, "not found")
            return
        n = int(self.headers.get("Content-Length", 0))
        payload = json.loads(self.rfile.read(n) or b"{}")
        topic = (payload.get("topic") or "").strip()
        if not topic:
            self._send(400, json.dumps({"error": "empty topic"}))
            return
        live = bool(payload.get("live"))
        if os.environ.get("NEBIUS_API_KEY") and not payload.get("mock"):
            llm = NebiusLLM(payload.get("model", "nvidia/llama-3.1-70b-instruct"))
        else:
            llm = MockLLM()
        report, steps = run_research(topic, llm, live=live)
        self._send(200, json.dumps({"report": report, "steps": steps},
                                    ensure_ascii=False))


def main():
    from argparse import ArgumentParser
    ap = ArgumentParser()
    ap.add_argument("--port", type=int, default=8090)
    ap.add_argument("--host", default="127.0.0.1")
    a = ap.parse_args()
    print(f"Nebius Agentic Research UI -> http://{a.host}:{a.port}")
    ThreadingHTTPServer((a.host, a.port), Handler).serve_forever()


if __name__ == "__main__":
    main()
