# EPUB Text Extraction for Illustrated Project Gutenberg Books

When a Project Gutenberg plain text download is **under 50KB** for a known substantial book, the text has likely been silently truncated — the real content lives in the EPUB or HTML editions, which may be 1-2MB. This is common for illustrated, scientific, or mathematical works.

## Detection

| Signal | Action |
|--------|--------|
| Plain text > 50KB | Use plain text — it's fine |
| Plain text < 50KB for a substantial book | Switch to EPUB extraction |
| Book has diagrams, figures, equations | Prefer EPUB from the start |

Mathematical/scientific works (Euclid's *Elements*, Newton's *Principia*, etc.) almost always need EPUB extraction because their figures are image-based and the plain text only captures captions.

## Extraction Method

EPUB files are standard ZIP archives containing XHTML. The CLI script (`scripts/gutenberg`) handles this automatically for the `pipeline` and `extract --format epub` commands.

### Manual Python Extraction

If you're working outside the CLI, this pattern extracts clean text from an EPUB:

```python
import zipfile
from html.parser import HTMLParser

class TextExtractor(HTMLParser):
    def __init__(self):
        super().__init__()
        self.text = []
        self.skip = False
    def handle_starttag(self, tag, attrs):
        if tag in ('script', 'style', 'svg'):
            self.skip = True
    def handle_endtag(self, tag):
        if tag in ('script', 'style', 'svg'):
            self.skip = False
        if tag in ('p', 'h1', 'h2', 'h3', 'h4', 'div', 'br', 'li'):
            self.text.append('\n')
    def handle_data(self, data):
        if not self.skip:
            self.text.append(data)

all_text = []
with zipfile.ZipFile('/tmp/book.epub', 'r') as z:
    for name in sorted(z.namelist()):
        if not (name.endswith('.html') or name.endswith('.xhtml')):
            continue
        content = z.read(name).decode('utf-8', errors='replace')
        parser = TextExtractor()
        parser.feed(content)
        all_text.append(''.join(parser.text))

full_text = '\n'.join(all_text)
```

## Expected Output

- 484K+ characters for a substantial multi-book work like Euclid's *Elements*
- Multiple HTML files (one per chapter/book/section) merged into a single text
- Some formatting artifacts from HTML stripping — clean with `re.sub(r'\n{3,}', '\n\n', text)` if needed

## Format Choice Decision Tree

```
Is the book illustrated, mathematical, or scientific?
├── YES → Prefer EPUB. The plain text may omit diagrams, figures, equations.
│         Use: `gutenberg download <id> --format epub`
│              `gutenberg extract <id> --format epub`
└── NO  → Plain text is fine for novels, essays, poetry, drama.
          Use: `gutenberg download <id> --format txt`
               `gutenberg extract <id>`
```

The `pipeline` command handles this automatically: it downloads plain text first, checks size, and falls back to EPUB extraction when the text is suspiciously small.
