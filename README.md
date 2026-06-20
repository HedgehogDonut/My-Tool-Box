# Python → PDF Converter

Convert Python source files into beautifully syntax-highlighted PDFs with VSCode-style themes.

Two versions — pick whichever suits you:

| | `converter.html` | `py_to_pdf.py` |
|---|---|---|
| **How to run** | Open in any browser | `python py_to_pdf.py` |
| **Dependencies** | None | `reportlab`, `pygments` |
| **Export** | Browser Print → Save as PDF | Generates `.pdf` directly |
| **Color control** | Individual color pickers per token | Preset themes only |

---

## `converter.html` — Browser App

No installation needed. Just open the file.

![Demo showing drag and drop interface with VSCode Dark+ theme](https://placeholder)

**Features:**
- Drag & drop any `.py` file onto the page
- 6 preset themes with one click
- 14 individual color pickers — background, text, keywords, strings, comments, functions, classes, numbers, built-ins, decorators, operators, parameters, line numbers
- Live preview updates instantly as you tweak colors
- Page size: A4, Letter, A3, Legal (portrait & landscape)
- Font size slider (6–16pt)
- Toggle line numbers and file header

**To export as PDF:**
1. Click **Print / Save as PDF**
2. In the print dialog, select **Save as PDF** as the destination
3. ⚠️ Enable **"Print backgrounds"** (or "Background graphics") — required for colors to appear

---

## `py_to_pdf.py` — Desktop GUI

Generates a real `.pdf` file directly, no browser needed.

**Requirements:**
```
pip install reportlab pygments
```

**Run:**
```bash
python py_to_pdf.py
```

**Features:**
- Native file picker
- 6 themes with color dot previews
- Theme preview window (live syntax-highlighted sample)
- Page size, orientation, font size controls
- Line numbers and file header options
- Progress bar during conversion

---

## Themes

| Theme | Style |
|---|---|
| **VSCode Dark+** | Classic dark editor (`#1E1E1E` bg) |
| **VSCode Light+** | Clean white editor |
| **Monokai** | High-contrast with olive/pink |
| **Dracula** | Purple-tinted dark |
| **Solarized Dark** | Low-contrast dark teal |
| **GitHub Light** | GitHub's code view colors |

---

## Files

```
.
├── converter.html   # Browser-based converter (open directly)
└── py_to_pdf.py     # Desktop GUI converter (requires Python)
```
