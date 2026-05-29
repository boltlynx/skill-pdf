# skill-pdf

[English](README.md) · [中文](README.zh-CN.md)

PDF skill for [BoltLynx](https://github.com/boltlynx) — read PDFs as Markdown and generate PDFs from HTML/CSS or Markdown.

## Install

```bash
curl -fsSL https://raw.githubusercontent.com/boltlynx/skill-pdf/main/install.sh | bash
```

This installs the tool to `~/.boltlynx/skills-bin/pdf/`. To register the skill with an agent, run `boltlynx skill install` in the project directory (see below), then enable it in the space settings via the `skill:pdf` kit.

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

The tool installs to `~/.boltlynx/skills-bin/pdf/`:

```
~/.boltlynx/skills-bin/pdf/
├── skill.json          # metadata (name, version, ...)
├── skill.md            # LLM-facing documentation
├── bin/
│   ├── pdf-read        # wrapper script
│   └── pdf-write       # wrapper script
├── src/
│   └── pdf_tool.py     # actual implementation
└── .venv/              # Python environment
```

To make the skill visible to an agent, register it in the project directory:

```bash
cd <your-project>
boltlynx skill install https://raw.githubusercontent.com/boltlynx/skill-pdf/main/skill.json
```

This writes `skill.json` + `skill.md` to `<your-project>/.boltlynx/skills/pdf/`.

## Uninstall

```bash
rm -rf ~/.boltlynx/skills-bin/pdf            # remove the tool
boltlynx skill uninstall pdf                 # unregister from the project
```

## License

MIT
