"""End-to-end protocol tests: run pdf_tool.py as a subprocess exactly
the way the bin wrappers do -- method via argv[1], args as a JSON line on
stdin, single JSON line on stdout.

This is the contract $.call({ cmd: '.../pdf-read', input: {...} }) relies on.
"""
import json
import os
import subprocess
import sys

import pytest

PDF_TOOL = os.path.join(os.path.dirname(__file__), "..", "src", "pdf_tool.py")


def run_tool(method, args):
    """Invoke pdf_tool.py <method> with args as a JSON line on stdin.
    Returns the parsed JSON response dict."""
    proc = subprocess.run(
        [sys.executable, PDF_TOOL, method],
        input=json.dumps(args),
        capture_output=True,
        text=True,
    )
    return json.loads(proc.stdout), proc


class TestProtocol:
    def test_write_then_read_roundtrip(self, tmp_path):
        output = str(tmp_path / "rt.pdf")
        wresp, wp = run_tool("write", {"content": "<h1>Hello</h1><p>World</p>", "output": output})
        assert "data" in wresp, wresp
        assert wresp["data"]["file"] == output
        assert os.path.exists(output)

        rresp, rp = run_tool("read", {"file": output})
        assert "data" in rresp, rresp
        assert "Hello" in rresp["data"]["content"]
        assert rresp["data"]["totalPages"] >= 1

    def test_unknown_method_returns_error(self):
        resp, proc = run_tool("frobnicate", {})
        assert "error" in resp
        assert "Unknown method" in resp["error"]

    def test_read_missing_args_returns_error(self):
        resp, proc = run_tool("read", {})
        assert "error" in resp

    def test_write_missing_output_returns_error(self):
        resp, proc = run_tool("write", {"content": "<h1>Hi</h1>"})
        assert "error" in resp

    def test_invalid_json_stdin_returns_error(self):
        proc = subprocess.run(
            [sys.executable, PDF_TOOL, "read"],
            input="this is not json",
            capture_output=True,
            text=True,
        )
        resp = json.loads(proc.stdout)
        assert "error" in resp
        assert "JSON" in resp["error"]

    def test_no_method_arg_returns_error(self):
        proc = subprocess.run(
            [sys.executable, PDF_TOOL],
            input="{}",
            capture_output=True,
            text=True,
        )
        resp = json.loads(proc.stdout)
        assert "error" in resp
