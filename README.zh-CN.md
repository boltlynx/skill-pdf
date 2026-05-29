# skill-pdf

[English](README.md) · [中文](README.zh-CN.md)

[BoltLynx](https://github.com/boltlynx) 的 PDF 技能包 —— 将 PDF 读取为 Markdown,以及从 HTML/CSS 或 Markdown 生成 PDF。

## 安装

```bash
curl -fsSL https://raw.githubusercontent.com/boltlynx/skill-pdf/main/install.sh | bash
```

这会把工具安装到 `~/.boltlynx/skills-bin/pdf/`。要让某个 agent 能用上这个技能,在项目目录下运行 `boltlynx skill install`(见下文),然后在 space 设置里通过 `skill:pdf` kit 启用它。

### 环境要求

- Python 3.12+
- [`uv`](https://astral.sh/uv)(安装脚本在缺失时会主动帮你装)
- PDF 写入(HTML→PDF)需要系统的 `pango` 库:
  - macOS:`brew install pango`
  - Linux:`apt install libpango-1.0-0 libpangocairo-1.0-0 libgdk-pixbuf2.0-0`(或 `yum install pango gdk-pixbuf2`)
- 中文/日文/韩文 PDF 需要 CJK 字体:
  - macOS:系统自带
  - Linux:`apt install fonts-noto-cjk`(或等价包)

## 安装后的目录结构

工具安装在 `~/.boltlynx/skills-bin/pdf/`:

```
~/.boltlynx/skills-bin/pdf/
├── skill.json          # 元数据(名称、版本……)
├── skill.md            # 面向 LLM 的说明文档
├── pdf-read            # 包装脚本
├── pdf-write           # 包装脚本
├── src/
│   └── pdf_tool.py     # 实际实现
└── .venv/              # Python 环境
```

要让 agent 看见这个技能,在项目目录下注册它:

```bash
cd <你的项目目录>
boltlynx skill install https://raw.githubusercontent.com/boltlynx/skill-pdf/main/skill.json
```

这会把 `skill.json` + `skill.md` 写入 `<你的项目目录>/.boltlynx/skills/pdf/`。

## 卸载

```bash
rm -rf ~/.boltlynx/skills-bin/pdf            # 删除工具本体
boltlynx skill uninstall pdf                 # 从项目中注销该技能
```

## 许可证

MIT
