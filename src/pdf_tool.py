#!/usr/bin/env python3
"""BoltLynx PDF skill — JSON lines over stdin/stdout.

Protocol:
  Request:  { "method": "read"|"write", "args": { ... } }
  Response: { "data": { ... } } | { "error": "message" }

Reads one JSON line from stdin, writes one JSON line to stdout, then exits.
"""
import sys
import os
import json
import platform  # noqa: E402

# macOS: brew installs C libraries to /opt/homebrew/lib (Apple Silicon) or /usr/local/lib (Intel).
# cffi.dlopen needs these paths to find pango/glib for weasyprint.
if platform.system() == "Darwin":
    brew_lib = "/opt/homebrew/lib" if platform.machine() == "arm64" else "/usr/local/lib"
    existing = os.environ.get("DYLD_FALLBACK_LIBRARY_PATH", "")
    os.environ["DYLD_FALLBACK_LIBRARY_PATH"] = f"{brew_lib}:{existing}" if existing else brew_lib

MIN_VERSIONS = {
    "pymupdf4llm": (0, 0, 17),
}

def check_deps():
    """Check required dependencies. Fail fast with clear message."""
    try:
        import pymupdf4llm
    except ImportError:
        return "pymupdf4llm not installed. Run: bash ~/.lynx/skills/pdf/install.sh (or reinstall via curl)"
    # Check version
    try:
        ver = tuple(int(x) for x in pymupdf4llm.__version__.split(".")[:3])
        if ver < MIN_VERSIONS["pymupdf4llm"]:
            return f"pymupdf4llm {pymupdf4llm.__version__} too old, need >={'.'.join(str(x) for x in MIN_VERSIONS['pymupdf4llm'])}. Run: bash ~/.lynx/skills/pdf/install.sh (or reinstall via curl)"
    except Exception:
        pass  # version parse failed, proceed anyway
    return None


def handle_read(args):
    """Extract text from PDF as Markdown."""
    import pymupdf4llm

    file_path = args.get("file")
    fetch = args.get("fetch")
    pages = args.get("pages")

    if not file_path and not fetch:
        return {"error": "Either 'file' or 'fetch' is required"}

    # Download if fetch
    if fetch:
        import urllib.request
        import tempfile
        url = fetch.get("url")
        if not url:
            return {"error": "fetch.url is required"}
        headers = fetch.get("headers", {})
        proxy = fetch.get("proxy")
        timeout = fetch.get("timeout", 60)

        req = urllib.request.Request(url, headers=headers)
        if proxy:
            handler = urllib.request.ProxyHandler({"http": proxy, "https": proxy})
            opener = urllib.request.build_opener(handler)
        else:
            opener = urllib.request.build_opener()

        try:
            resp = opener.open(req, timeout=timeout)
            tmp = tempfile.NamedTemporaryFile(suffix=".pdf", delete=False)
            tmp.write(resp.read())
            tmp.close()
            file_path = tmp.name
        except Exception as e:
            return {"error": f"Failed to download PDF: {e}"}

    # Extract
    try:
        kwargs = {}
        if pages:
            kwargs["pages"] = [p - 1 for p in pages]  # pymupdf uses 0-based

        md = pymupdf4llm.to_markdown(file_path, **kwargs)

        # Get page count
        import pymupdf
        doc = pymupdf.open(file_path)
        total_pages = len(doc)
        doc.close()

        return {"data": {"content": md, "totalPages": total_pages}}
    except Exception as e:
        return {"error": f"Failed to extract PDF: {e}"}


def detect_format(content, file_path, explicit_format):
    """Detect content format: 'html' or 'md'."""
    if explicit_format:
        return explicit_format
    if file_path:
        ext = os.path.splitext(file_path)[1].lower()
        if ext in ('.md', '.markdown', '.mdown', '.mkd'):
            return 'md'
        return 'html'
    # Content string: check for HTML markers
    if content:
        stripped = content.strip()[:200].lower()
        if stripped.startswith('<!doctype') or stripped.startswith('<html') or '<div' in stripped or '<body' in stripped:
            return 'html'
        return 'md'
    return 'html'


def markdown_to_html(md_text):
    """Convert Markdown to styled HTML with code highlighting and math support."""
    from markdown_it import MarkdownIt
    from mdit_py_plugins.dollarmath import dollarmath_plugin
    from pygments import highlight as pyg_highlight
    from pygments.lexers import get_lexer_by_name, TextLexer
    from pygments.formatters import HtmlFormatter

    md = MarkdownIt("commonmark", {"highlight": _highlight_code})
    md.enable("table")
    md.enable("strikethrough")
    dollarmath_plugin(md)

    body_html = md.render(md_text)

    # Generate Pygments CSS
    formatter = HtmlFormatter(style="github-dark")
    pygments_css = formatter.get_style_defs(".highlight")

    html = f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<style>
body {{
    font-family: "Hiragino Sans GB", "Noto Sans CJK SC", "Microsoft YaHei", -apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica, Arial, sans-serif;
    line-height: 1.6;
    max-width: 800px;
    margin: 0 auto;
    padding: 2cm;
    color: #24292f;
}}
h1 {{ border-bottom: 1px solid #d0d7de; padding-bottom: 0.3em; }}
h2 {{ border-bottom: 1px solid #d0d7de; padding-bottom: 0.3em; }}
code {{
    background: #f6f8fa;
    padding: 0.2em 0.4em;
    border-radius: 3px;
    font-size: 85%;
    font-family: "SFMono-Regular", Consolas, "Liberation Mono", Menlo, monospace;
}}
pre {{
    background: #0d1117;
    color: #e6edf3;
    padding: 16px;
    border-radius: 6px;
    overflow-x: auto;
    line-height: 1.45;
}}
pre code {{
    background: none;
    padding: 0;
    color: inherit;
    font-size: 85%;
}}
blockquote {{
    border-left: 4px solid #d0d7de;
    margin: 0;
    padding: 0 1em;
    color: #656d76;
}}
table {{
    border-collapse: collapse;
    width: 100%;
    margin: 1em 0;
}}
th, td {{
    border: 1px solid #d0d7de;
    padding: 6px 13px;
}}
th {{
    background: #f6f8fa;
    font-weight: 600;
}}
img {{ max-width: 100%; }}
.math {{ font-style: italic; }}
{pygments_css}
</style>
</head>
<body>
{body_html}
</body>
</html>"""
    return html


def _highlight_code(code, lang, attrs):
    """Highlight code block with Pygments."""
    from pygments import highlight as pyg_highlight
    from pygments.lexers import get_lexer_by_name, TextLexer
    from pygments.formatters import HtmlFormatter

    try:
        lexer = get_lexer_by_name(lang) if lang else TextLexer()
    except Exception:
        lexer = TextLexer()
    formatter = HtmlFormatter(nowrap=False, cssclass="highlight")
    return pyg_highlight(code, lexer, formatter)


def handle_write(args):
    """Generate PDF from HTML/CSS or Markdown content."""
    content = args.get("content")
    file_path = args.get("file")
    output = args.get("output")
    fmt = args.get("format")

    if not output:
        return {"error": "'output' is required"}
    if not content and not file_path:
        return {"error": "Either 'content' or 'file' is required"}

    try:
        import weasyprint
    except (ImportError, OSError) as e:
        return {"error": f"weasyprint not available: {e}. Run: bash ~/.lynx/skills/pdf/install.sh (or reinstall via curl)"}

    try:
        # Read file content if needed
        if file_path and not content:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

        # Detect and convert format
        detected_format = detect_format(content, file_path, fmt)
        if detected_format == "md":
            try:
                html_content = markdown_to_html(content)
            except ImportError as e:
                return {"error": f"Markdown dependencies not available: {e}. Run: bash ~/.lynx/skills/pdf/install.sh (or reinstall via curl)"}
        else:
            html_content = content

        doc = weasyprint.HTML(string=html_content)
        doc.write_pdf(output)

        # Count pages
        import pymupdf
        pdf_doc = pymupdf.open(output)
        pages = len(pdf_doc)
        pdf_doc.close()

        return {"data": {"file": output, "pages": pages}}
    except Exception as e:
        return {"error": f"Failed to generate PDF: {e}"}


def main():
    # Method comes from argv[1] (set by bin wrapper); args come from stdin JSON.
    if len(sys.argv) < 2:
        json.dump({"error": "Usage: pdf_tool.py <method> (called via bin wrapper)"}, sys.stdout)
        sys.stdout.write("\n")
        sys.exit(1)
    method = sys.argv[1]

    # Check dependencies first
    err = check_deps()
    if err:
        json.dump({"error": err}, sys.stdout)
        sys.stdout.write("\n")
        sys.stdout.flush()
        sys.exit(1)

    # Read args from stdin
    try:
        line = sys.stdin.read()
        if not line.strip():
            args = {}
        else:
            args = json.loads(line)
    except json.JSONDecodeError as e:
        json.dump({"error": f"Invalid JSON: {e}"}, sys.stdout)
        sys.stdout.write("\n")
        sys.exit(1)

    if method == "read":
        result = handle_read(args)
    elif method == "write":
        result = handle_write(args)
    else:
        result = {"error": f"Unknown method: {method}"}

    json.dump(result, sys.stdout)
    sys.stdout.write("\n")
    sys.stdout.flush()


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        json.dump({"error": f"Unexpected error: {e}"}, sys.stdout)
        sys.stdout.write("\n")
        sys.stdout.flush()
        sys.exit(1)
