#!/bin/bash
set -e

# Install location (per BoltLynx skill convention)
SKILL_DIR="$HOME/.boltlynx/skills-bin/pdf"
VENV_DIR="$SKILL_DIR/.venv"
SRC_URL="https://raw.githubusercontent.com/boltlynx/skill-pdf/main"

echo "Installing skill-pdf to $SKILL_DIR ..."
mkdir -p "$SKILL_DIR/src"

# ── 1. Fetch files (skill.json + skill.md + src + bin wrappers) ──
download() {
  local rel="$1"
  local dest="$2"
  if [ -f "$(dirname "$0")/$rel" ]; then
    # local install (running from cloned repo)
    cp "$(dirname "$0")/$rel" "$dest"
  else
    curl -fsSL "$SRC_URL/$rel" -o "$dest"
  fi
}

download skill.json "$SKILL_DIR/skill.json"
download skill.md "$SKILL_DIR/skill.md"
download src/pdf_tool.py "$SKILL_DIR/src/pdf_tool.py"

# ── 2. Check uv ──
if ! command -v uv &>/dev/null; then
  echo "Installing uv..."
  curl -LsSf https://astral.sh/uv/install.sh | sh
  export PATH="$HOME/.local/bin:$PATH"
fi

# ── 3. Python 3.12 ──
echo "Ensuring Python 3.12..."
uv python install 3.12 -q 2>/dev/null || true

# ── 4. System dependencies (pango — needed for HTML→PDF) ──
if ! pkg-config --exists pangocairo 2>/dev/null; then
  if ldconfig -p 2>/dev/null | grep -q libpango; then
    : # available
  elif command -v brew &>/dev/null; then
    echo "Installing pango via brew..."
    brew install pango
  elif command -v apt-get &>/dev/null && sudo -n true 2>/dev/null; then
    echo "Installing pango via apt..."
    sudo apt-get install -y libpango-1.0-0 libpangocairo-1.0-0 libgdk-pixbuf2.0-0
  elif command -v yum &>/dev/null && sudo -n true 2>/dev/null; then
    echo "Installing pango via yum..."
    sudo yum install -y pango gdk-pixbuf2
  else
    echo "" >&2
    echo "⚠ Pango not found. PDF read works, but PDF write (HTML→PDF) needs pango." >&2
    if command -v apt-get &>/dev/null; then
      echo "  Install:  sudo apt install libpango-1.0-0 libpangocairo-1.0-0 libgdk-pixbuf2.0-0" >&2
    elif command -v yum &>/dev/null; then
      echo "  Install:  sudo yum install pango gdk-pixbuf2" >&2
    elif command -v brew &>/dev/null; then
      echo "  Install:  brew install pango" >&2
    fi
    echo "" >&2
  fi
fi

# CJK fonts (Linux check)
if [ "$(uname)" = "Linux" ]; then
  if ! fc-list :lang=zh family 2>/dev/null | grep -qi "noto\|cjk\|wqy\|wenquanyi"; then
    echo "" >&2
    echo "⚠ CJK fonts not found. Chinese/Japanese/Korean PDFs may render incorrectly." >&2
    if command -v apt-get &>/dev/null; then
      echo "  Install:  sudo apt install fonts-noto-cjk" >&2
    elif command -v yum &>/dev/null; then
      echo "  Install:  sudo yum install google-noto-sans-cjk-fonts" >&2
    fi
    echo "" >&2
  fi
fi

# ── 5. Python venv + dependencies ──
echo "Setting up Python environment..."
uv venv "$VENV_DIR" --python 3.12 --allow-existing -q
uv pip install --python "$VENV_DIR/bin/python" \
  "pymupdf4llm>=0.0.17" "weasyprint>=62.0" \
  "markdown-it-py>=3.0" "mdit_py_plugins>=0.4" "pygments>=2.17" -q

# ── 6. bin wrappers ──
cat > "$SKILL_DIR/pdf-read" << 'EOF'
#!/bin/bash
exec "$HOME/.boltlynx/skills-bin/pdf/.venv/bin/python" "$HOME/.boltlynx/skills-bin/pdf/src/pdf_tool.py" read
EOF
chmod +x "$SKILL_DIR/pdf-read"

cat > "$SKILL_DIR/pdf-write" << 'EOF'
#!/bin/bash
exec "$HOME/.boltlynx/skills-bin/pdf/.venv/bin/python" "$HOME/.boltlynx/skills-bin/pdf/src/pdf_tool.py" write
EOF
chmod +x "$SKILL_DIR/pdf-write"

echo ""
echo "✓ skill-pdf installed at $SKILL_DIR"
echo ""
echo "Enable in any agent's space settings: kits → check 'pdf'."
