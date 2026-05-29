"""Unit tests for the flat pdf_tool.py interface.

handle_read / handle_write take a dict of args and ALWAYS return a dict:
  success -> {"data": {...}}
  failure -> {"error": "..."}   (they never raise)
"""
import os

from pdf_tool import handle_read, handle_write


# --- Write tests ---

class TestHandleWrite:
    def test_write_simple_html(self, tmp_path):
        output = str(tmp_path / "out.pdf")
        result = handle_write({"content": "<h1>Hello World</h1>", "output": output})
        assert "data" in result, result
        assert result["data"]["file"] == output
        assert result["data"]["pages"] >= 1
        assert os.path.exists(output)
        assert os.path.getsize(output) > 0

    def test_write_chinese(self, tmp_path):
        output = str(tmp_path / "cn.pdf")
        html = "<html><body><h1>中文标题</h1><p>这是一段中文内容。</p></body></html>"
        result = handle_write({"content": html, "output": output})
        assert "data" in result, result
        assert result["data"]["pages"] >= 1
        assert os.path.exists(output)

    def test_write_from_file(self, tmp_path):
        html_file = str(tmp_path / "input.html")
        output = str(tmp_path / "out.pdf")
        with open(html_file, "w") as f:
            f.write("<h1>From File</h1><p>Content here.</p>")
        result = handle_write({"file": html_file, "output": output})
        assert "data" in result, result
        assert result["data"]["pages"] >= 1

    def test_write_markdown(self, tmp_path):
        output = str(tmp_path / "md.pdf")
        result = handle_write({"content": "# Title\n\nA paragraph.", "format": "md", "output": output})
        assert "data" in result, result
        assert result["data"]["pages"] >= 1

    def test_write_no_output_returns_error(self):
        result = handle_write({"content": "<h1>Hi</h1>"})
        assert "error" in result
        assert "output" in result["error"]

    def test_write_no_input_returns_error(self, tmp_path):
        output = str(tmp_path / "out.pdf")
        result = handle_write({"output": output})
        assert "error" in result
        assert "content" in result["error"] or "file" in result["error"]


# --- Read tests ---

class TestHandleRead:
    def _sample_pdf(self, tmp_path):
        output = str(tmp_path / "sample.pdf")
        html = (
            "<html><body>"
            "<h1>Chapter 1</h1>"
            "<p>First paragraph with some text.</p>"
            "<h2>Section 1.1</h2>"
            "<p>Second paragraph.</p>"
            "<table><tr><th>Name</th><th>Value</th></tr>"
            "<tr><td>Alpha</td><td>100</td></tr>"
            "<tr><td>Beta</td><td>200</td></tr></table>"
            "</body></html>"
        )
        r = handle_write({"content": html, "output": output})
        assert "data" in r, r
        return output

    def test_read_returns_content(self, tmp_path):
        pdf = self._sample_pdf(tmp_path)
        result = handle_read({"file": pdf})
        assert "data" in result, result
        assert "content" in result["data"]
        assert "totalPages" in result["data"]
        assert result["data"]["totalPages"] >= 1
        assert len(result["data"]["content"]) > 0

    def test_read_extracts_headings(self, tmp_path):
        pdf = self._sample_pdf(tmp_path)
        content = handle_read({"file": pdf})["data"]["content"]
        assert "Chapter 1" in content
        assert "Section 1.1" in content

    def test_read_extracts_text(self, tmp_path):
        pdf = self._sample_pdf(tmp_path)
        content = handle_read({"file": pdf})["data"]["content"]
        assert "First paragraph" in content

    def test_read_extracts_table(self, tmp_path):
        pdf = self._sample_pdf(tmp_path)
        content = handle_read({"file": pdf})["data"]["content"]
        assert "Alpha" in content
        assert "100" in content

    def test_read_specific_pages(self, tmp_path):
        pdf = self._sample_pdf(tmp_path)
        result = handle_read({"file": pdf, "pages": [1]})
        assert "data" in result, result
        assert result["data"]["totalPages"] >= 1
        assert len(result["data"]["content"]) > 0

    def test_read_nonexistent_file_returns_error(self):
        result = handle_read({"file": "/nonexistent/path.pdf"})
        assert "error" in result

    def test_read_no_input_returns_error(self):
        result = handle_read({})
        assert "error" in result
        assert "file" in result["error"] or "fetch" in result["error"]
