You have PDF capabilities: read PDFs to Markdown, and generate PDFs from HTML/CSS or Markdown.

The skill provides two commands invoked via `$.call`. Both follow JSON stdin/stdout protocol.

## pdf-read

Extract text content from a PDF as Markdown.

```typescript
interface PdfReadInput {
  /** Path to local PDF file (file or fetch required) */
  file?: string
  /** Or fetch from URL */
  fetch?: { url: string; headers?: Record<string, string>; proxy?: string; timeout?: number }
  /** 1-based page numbers (default: all pages) */
  pages?: number[]
}

interface PdfReadResult {
  content: string      // Markdown text
  totalPages: number
}
```

```js
const r = await $.call({
  cmd: '~/.boltlynx/skills-bin/pdf/bin/pdf-read',
  input: { file: 'report.pdf' },
})
// r.content is markdown text, r.totalPages is page count
```

## pdf-write

Generate a PDF from HTML/CSS or Markdown.

```typescript
interface PdfWriteInput {
  /** Source file path (auto-detected by extension: .md/.markdown → markdown, else HTML) */
  file?: string
  /** Or raw content string */
  content?: string
  /** Force format detection */
  format?: 'html' | 'md'
  /** Output PDF path (required) */
  output: string
}

interface PdfWriteResult {
  file: string
  pages: number
}
```

```js
// From Markdown file
await $.call({
  cmd: '~/.boltlynx/skills-bin/pdf/bin/pdf-write',
  input: { file: 'docs/design.md', output: 'design.pdf' },
})

// From HTML for full layout control
await $.call({
  cmd: '~/.boltlynx/skills-bin/pdf/bin/pdf-write',
  input: { content: '<h1>Title</h1><p>Body</p>', output: 'out.pdf' },
})
```

## Choosing format

- **Markdown** — easiest for documents, reports, articles. Supports tables, code blocks with syntax highlighting, math formulas (`$E=mc^2$`).
- **HTML/CSS** — when you need precise layout: slides, custom page sizes, page breaks, CJK fonts. Standard web CSS applies.

For HTML with Chinese content, use `font-family: "Noto Sans CJK SC", "Hiragino Sans GB", sans-serif`.
