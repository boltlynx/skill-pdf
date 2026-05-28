# skill-pdf

PDF skill for [BoltLynx](https://github.com/boltlynx) — read PDFs as Markdown and generate PDFs from HTML/CSS or Markdown.

## Install

```bash
curl -fsSL https://raw.githubusercontent.com/boltlynx/skill-pdf/main/install.sh | bash
```

This installs to `~/.lynx/skills/pdf/`. Once installed, enable in any agent's space settings via the `skill:pdf` kit.

### Requirements

- Python 3.12+
- [`uv`](https://astral.sh/uv) (the installer will offer to install it if missing)
- For PDF write (HTML→PDF): system `pango` library
  - macOS: `brew install pango`
  - Linux: `apt install libpango-1.0-0 libpangocairo-1.0-0 libgdk-pixbuf2.0-0` (or `yum install pango gdk-pixbuf2`)
- For Chinese/Japanese/Korean PDFs: CJK fonts
  - macOS: built-in
  - Linux: `apt install fonts-noto-cjk` (or equivalent)

## Layout (after install)

```
~/.lynx/skills/pdf/
├── skill.json          # metadata (name, version, ...)
├── skill.md            # LLM-facing documentation
├── bin/
│   ├── pdf-read        # wrapper script
│   └── pdf-write       # wrapper script
├── src/
│   └── pdf_tool.py     # actual implementation
└── .venv/              # Python environment
```

## Uninstall

```bash
rm -rf ~/.lynx/skills/pdf
```

## License

MIT
