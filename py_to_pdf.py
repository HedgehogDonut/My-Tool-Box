#!/usr/bin/env python3
"""
Python → PDF Converter
Converts Python source files to beautifully styled PDFs with VSCode-like themes.
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
import threading

try:
    from reportlab.lib.pagesizes import letter, A4, A3, legal
    from reportlab.pdfgen import canvas as rl_canvas
    from reportlab.lib.colors import Color
    from reportlab.lib.units import inch
    from pygments import lex
    from pygments.lexers import PythonLexer
    from pygments.token import Token
except ImportError:
    import subprocess, sys
    subprocess.check_call([sys.executable, "-m", "pip", "install", "reportlab", "pygments"])
    from reportlab.lib.pagesizes import letter, A4, A3, legal
    from reportlab.pdfgen import canvas as rl_canvas
    from reportlab.lib.colors import Color
    from reportlab.lib.units import inch
    from pygments import lex
    from pygments.lexers import PythonLexer
    from pygments.token import Token


# ──────────────────────────────────────────────────────────────────────────────
# THEMES
# ──────────────────────────────────────────────────────────────────────────────

THEMES = {
    "VSCode Dark+": {
        "bg":        "#1E1E1E",
        "gutter_bg": "#1E1E1E",
        "gutter_fg": "#858585",
        "default":   "#D4D4D4",
        "header_bg": "#252526",
        "header_fg": "#CCCCCC",
        Token.Keyword:              "#569CD6",
        Token.Keyword.Namespace:    "#C586C0",
        Token.Keyword.Type:         "#4EC9B0",
        Token.Name.Builtin:         "#4EC9B0",
        Token.Name.Function:        "#DCDCAA",
        Token.Name.Class:           "#4EC9B0",
        Token.Name.Decorator:       "#DCDCAA",
        Token.Name.Exception:       "#4EC9B0",
        Token.Literal.String:       "#CE9178",
        Token.Literal.String.Doc:   "#6A9955",
        Token.Literal.Number:       "#B5CEA8",
        Token.Comment:              "#6A9955",
        Token.Operator:             "#D4D4D4",
        Token.Punctuation:          "#D4D4D4",
        Token.Name:                 "#D4D4D4",
    },
    "VSCode Light+": {
        "bg":        "#FFFFFF",
        "gutter_bg": "#F8F8F8",
        "gutter_fg": "#999999",
        "default":   "#000000",
        "header_bg": "#F3F3F3",
        "header_fg": "#333333",
        Token.Keyword:              "#0000FF",
        Token.Keyword.Namespace:    "#AF00DB",
        Token.Keyword.Type:         "#267F99",
        Token.Name.Builtin:         "#267F99",
        Token.Name.Function:        "#795E26",
        Token.Name.Class:           "#267F99",
        Token.Name.Decorator:       "#795E26",
        Token.Name.Exception:       "#267F99",
        Token.Literal.String:       "#A31515",
        Token.Literal.String.Doc:   "#008000",
        Token.Literal.Number:       "#098658",
        Token.Comment:              "#008000",
        Token.Operator:             "#000000",
        Token.Punctuation:          "#000000",
        Token.Name:                 "#000000",
    },
    "Monokai": {
        "bg":        "#272822",
        "gutter_bg": "#272822",
        "gutter_fg": "#75715E",
        "default":   "#F8F8F2",
        "header_bg": "#3E3D32",
        "header_fg": "#F8F8F2",
        Token.Keyword:            "#F92672",
        Token.Keyword.Namespace:  "#F92672",
        Token.Keyword.Type:       "#66D9EF",
        Token.Name.Builtin:       "#66D9EF",
        Token.Name.Function:      "#A6E22E",
        Token.Name.Class:         "#A6E22E",
        Token.Name.Decorator:     "#A6E22E",
        Token.Literal.String:     "#E6DB74",
        Token.Literal.String.Doc: "#75715E",
        Token.Literal.Number:     "#AE81FF",
        Token.Comment:            "#75715E",
        Token.Operator:           "#F92672",
        Token.Punctuation:        "#F8F8F2",
        Token.Name:               "#F8F8F2",
    },
    "Dracula": {
        "bg":        "#282A36",
        "gutter_bg": "#21222C",
        "gutter_fg": "#6272A4",
        "default":   "#F8F8F2",
        "header_bg": "#21222C",
        "header_fg": "#F8F8F2",
        Token.Keyword:            "#FF79C6",
        Token.Keyword.Namespace:  "#FF79C6",
        Token.Keyword.Type:       "#8BE9FD",
        Token.Name.Builtin:       "#8BE9FD",
        Token.Name.Function:      "#50FA7B",
        Token.Name.Class:         "#8BE9FD",
        Token.Name.Decorator:     "#50FA7B",
        Token.Literal.String:     "#F1FA8C",
        Token.Literal.String.Doc: "#6272A4",
        Token.Literal.Number:     "#BD93F9",
        Token.Comment:            "#6272A4",
        Token.Operator:           "#FF79C6",
        Token.Punctuation:        "#F8F8F2",
        Token.Name:               "#F8F8F2",
    },
    "Solarized Dark": {
        "bg":        "#002B36",
        "gutter_bg": "#073642",
        "gutter_fg": "#586E75",
        "default":   "#839496",
        "header_bg": "#073642",
        "header_fg": "#93A1A1",
        Token.Keyword:        "#859900",
        Token.Name.Builtin:   "#2AA198",
        Token.Name.Function:  "#268BD2",
        Token.Name.Class:     "#268BD2",
        Token.Literal.String: "#2AA198",
        Token.Literal.Number: "#D33682",
        Token.Comment:        "#586E75",
        Token.Operator:       "#657B83",
        Token.Name:           "#839496",
    },
    "GitHub Light": {
        "bg":        "#FFFFFF",
        "gutter_bg": "#F6F8FA",
        "gutter_fg": "#8B949E",
        "default":   "#24292E",
        "header_bg": "#F6F8FA",
        "header_fg": "#586069",
        Token.Keyword:        "#D73A49",
        Token.Name.Builtin:   "#005CC5",
        Token.Name.Function:  "#6F42C1",
        Token.Name.Class:     "#6F42C1",
        Token.Literal.String: "#032F62",
        Token.Literal.Number: "#005CC5",
        Token.Comment:        "#6A737D",
        Token.Operator:       "#D73A49",
        Token.Name:           "#24292E",
    },
}

PAGE_SIZES = {
    'Letter (8.5×11")': letter,
    "A4 (210×297mm)":   A4,
    "A3 (297×420mm)":   A3,
    'Legal (8.5×14")':  legal,
}

# Markdown document colors per code theme
MD_DOC_COLORS = {
    "VSCode Dark+":   {"bg":"#1e1e1e","text":"#d4d4d4","h1":"#4ec9b0","h2":"#569cd6","h3":"#dcdcaa","code_bg":"#252526","code_text":"#ce9178","bq_border":"#3c5a78","bq_bg":"#1e2b33","link":"#4ec9b0","hr":"#3c3c3c"},
    "VSCode Light+":  {"bg":"#ffffff","text":"#000000","h1":"#267f99","h2":"#0000ff","h3":"#795e26","code_bg":"#f3f3f3","code_text":"#a31515","bq_border":"#cccccc","bq_bg":"#f8f8f8","link":"#0000ff","hr":"#e0e0e0"},
    "Monokai":        {"bg":"#272822","text":"#f8f8f2","h1":"#a6e22e","h2":"#66d9ef","h3":"#e6db74","code_bg":"#3e3d32","code_text":"#e6db74","bq_border":"#75715e","bq_bg":"#3e3d32","link":"#66d9ef","hr":"#3e3d32"},
    "Dracula":        {"bg":"#282a36","text":"#f8f8f2","h1":"#50fa7b","h2":"#8be9fd","h3":"#f1fa8c","code_bg":"#21222c","code_text":"#f1fa8c","bq_border":"#6272a4","bq_bg":"#21222c","link":"#8be9fd","hr":"#44475a"},
    "Solarized Dark": {"bg":"#002b36","text":"#839496","h1":"#268bd2","h2":"#2aa198","h3":"#859900","code_bg":"#073642","code_text":"#2aa198","bq_border":"#586e75","bq_bg":"#073642","link":"#268bd2","hr":"#073642"},
    "GitHub Light":   {"bg":"#ffffff","text":"#24292e","h1":"#1f2328","h2":"#1f2328","h3":"#555555","code_bg":"#f6f8fa","code_text":"#24292e","bq_border":"#d0d7de","bq_bg":"#f6f8fa","link":"#0969da","hr":"#d0d7de"},
}


# ──────────────────────────────────────────────────────────────────────────────
# PDF GENERATION
# ──────────────────────────────────────────────────────────────────────────────

# ── Markdown HTML → reportlab parser ──────────────────────────────────────────

class _MdHTMLParser:
    """Converts HTML (from markdown()) into a list of reportlab Platypus flowables."""

    def __init__(self, styles: dict, link_color):
        from html.parser import HTMLParser as _HP

        self._styles = styles
        self._link_color = link_color
        self.story: list = []

        class _Inner(_HP):
            def __init__(inner, outer):
                super().__init__(convert_charrefs=True)
                inner.o = outer
            def handle_starttag(inner, tag, attrs): inner.o._start(tag, dict(attrs))
            def handle_endtag(inner, tag):          inner.o._end(tag)
            def handle_data(inner, data):           inner.o._data(data)

        self._p = _Inner(self)
        self._tag_stack: list[str] = []
        self._buf = ""
        self._in_pre = False
        self._pre_buf = ""
        self._list_stack: list[list] = []
        self._in_bq = False
        self._bq_parts: list[str] = []

    def feed(self, html: str):
        self._p.feed(html)

    def get_story(self) -> list:
        self._flush_buf("body")
        return self.story

    # ── internal ──────────────────────────────────────────────────────────────

    @staticmethod
    def _esc(t: str) -> str:
        return t.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

    def _flush_buf(self, style_key: str = "body"):
        from reportlab.platypus import Paragraph, Spacer
        text = self._buf.strip()
        self._buf = ""
        if text:
            self.story.append(Paragraph(text, self._styles[style_key]))
            self.story.append(Spacer(1, 4))

    def _start(self, tag: str, attrs: dict):
        from reportlab.platypus import HRFlowable, Spacer
        self._tag_stack.append(tag)

        if tag in ("h1","h2","h3","h4","h5","h6"):
            self._flush_buf("body")
        elif tag == "pre":
            self._flush_buf("body")
            self._in_pre = True; self._pre_buf = ""
        elif tag in ("ul","ol"):
            self._flush_buf("body")
            self._list_stack.append([tag, 0])
        elif tag == "li":
            self._flush_buf("body")
        elif tag == "blockquote":
            self._flush_buf("body")
            self._in_bq = True; self._bq_parts = []
        elif tag == "hr":
            self._flush_buf("body")
            self.story.append(HRFlowable(width="100%", thickness=0.5,
                                          color=self._styles["_hr_color"]))
            self.story.append(Spacer(1, 6))
        elif tag == "br":
            self._buf += "<br/>"
        elif tag in ("strong","b"):
            self._buf += "<b>"
        elif tag in ("em","i"):
            self._buf += "<i>"
        elif tag == "code" and not self._in_pre:
            self._buf += '<font name="Courier">'
        elif tag == "a":
            href = attrs.get("href","")
            self._buf += f'<link href="{self._esc(href)}">'
        elif tag == "img":
            self._buf += f'[{self._esc(attrs.get("alt","image"))}]'

    def _end(self, tag: str):
        from reportlab.platypus import Paragraph, Spacer, Preformatted
        from reportlab.lib.styles import ParagraphStyle
        if self._tag_stack and self._tag_stack[-1] == tag:
            self._tag_stack.pop()

        if tag in ("h1","h2","h3","h4","h5","h6"):
            text = self._buf.strip(); self._buf = ""
            if text:
                sk = {"h1":"h1","h2":"h2"}.get(tag,"h3")
                self.story.append(Spacer(1, 6))
                self.story.append(Paragraph(text, self._styles[sk]))
                self.story.append(Spacer(1, 4))
        elif tag == "p":
            text = self._buf.strip(); self._buf = ""
            if text:
                if self._in_bq:
                    self._bq_parts.append(text)
                else:
                    sk = "li_body" if self._list_stack else "body"
                    self.story.append(Paragraph(text, self._styles[sk]))
                    self.story.append(Spacer(1, 4))
        elif tag == "pre":
            self._in_pre = False
            code = self._pre_buf.strip("\n")
            if code:
                self.story.append(Preformatted(code, self._styles["code"]))
                self.story.append(Spacer(1, 6))
            self._pre_buf = ""
        elif tag == "li":
            text = self._buf.strip(); self._buf = ""
            if text and self._list_stack:
                lt, cnt = self._list_stack[-1]
                if lt == "ul":
                    bullet = "•  "
                else:
                    self._list_stack[-1][1] = cnt + 1
                    bullet = f"{cnt+1}.  "
                indent = (len(self._list_stack)-1) * 18
                li_style = ParagraphStyle("_li", parent=self._styles["body"],
                                          leftIndent=indent+16,
                                          spaceBefore=1, spaceAfter=1)
                self.story.append(Paragraph(bullet + text, li_style))
        elif tag in ("ul","ol"):
            if self._list_stack: self._list_stack.pop()
            self.story.append(Spacer(1, 5))
        elif tag == "blockquote":
            self._in_bq = False
            text = " ".join(self._bq_parts).strip()
            if text:
                self.story.append(Paragraph(text, self._styles["bq"]))
                self.story.append(Spacer(1, 4))
            self._bq_parts = []
        elif tag in ("strong","b"):  self._buf += "</b>"
        elif tag in ("em","i"):      self._buf += "</i>"
        elif tag == "code" and not self._in_pre: self._buf += "</font>"
        elif tag == "a":             self._buf += "</link>"

    def _data(self, data: str):
        if self._in_pre:
            self._pre_buf += data
        else:
            self._buf += self._esc(data)


def generate_md_pdf(
    md_file: str,
    output_file: str,
    theme_name: str,
    page_size_name: str,
    orientation: str,
    font_size: int,
    show_header: bool,
    progress_callback=None,
):
    """Generate a styled PDF from a Markdown file."""
    try:
        import markdown as _md
    except ImportError:
        import subprocess, sys
        subprocess.check_call([sys.executable, "-m", "pip", "install", "markdown"])
        import markdown as _md

    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
    from reportlab.lib.styles import ParagraphStyle

    mc = MD_DOC_COLORS.get(theme_name, MD_DOC_COLORS["GitHub Light"])

    bg_c      = _hex_to_color(mc["bg"])
    text_c    = _hex_to_color(mc["text"])
    h1_c      = _hex_to_color(mc["h1"])
    h2_c      = _hex_to_color(mc["h2"])
    h3_c      = _hex_to_color(mc["h3"])
    code_bg_c = _hex_to_color(mc["code_bg"])
    code_c    = _hex_to_color(mc["code_text"])
    bq_bg_c   = _hex_to_color(mc["bq_bg"])
    bq_bdr_c  = _hex_to_color(mc["bq_border"])
    link_c    = _hex_to_color(mc["link"])
    hr_c      = _hex_to_color(mc["hr"])

    base_size = PAGE_SIZES[page_size_name]
    if orientation == "Landscape":
        from reportlab.lib.pagesizes import landscape
        page_size = landscape(base_size)
    else:
        page_size = base_size
    page_w, page_h = page_size

    margin   = 0.9 * inch
    header_h = 0.4 * inch if show_header else 0

    fs = font_size
    styles_map = {
        "body":    ParagraphStyle("body",   fontName="Helvetica",          fontSize=fs,      textColor=text_c,  leading=fs*1.65, spaceAfter=6),
        "h1":      ParagraphStyle("h1",     fontName="Helvetica-Bold",     fontSize=fs*2.0,  textColor=h1_c,    leading=fs*2.5,  spaceBefore=12, spaceAfter=8),
        "h2":      ParagraphStyle("h2",     fontName="Helvetica-Bold",     fontSize=fs*1.5,  textColor=h2_c,    leading=fs*2.0,  spaceBefore=10, spaceAfter=6),
        "h3":      ParagraphStyle("h3",     fontName="Helvetica-Bold",     fontSize=fs*1.2,  textColor=h3_c,    leading=fs*1.7,  spaceBefore=8,  spaceAfter=4),
        "code":    ParagraphStyle("code",   fontName="Courier",            fontSize=fs*0.85, textColor=code_c,  leading=fs*1.3,  backColor=code_bg_c, leftIndent=10, rightIndent=10, spaceAfter=8, spaceBefore=6, borderPadding=8),
        "bq":      ParagraphStyle("bq",     fontName="Helvetica-Oblique",  fontSize=fs,      textColor=text_c,  leading=fs*1.65, leftIndent=14, borderColor=bq_bdr_c, borderWidth=3, borderPadding=(4,8,4,10), backColor=bq_bg_c, spaceAfter=8),
        "li_body": ParagraphStyle("li_body",fontName="Helvetica",          fontSize=fs,      textColor=text_c,  leading=fs*1.65, spaceBefore=1, spaceAfter=1),
        "_hr_color": hr_c,
    }

    with open(md_file, "r", encoding="utf-8", errors="replace") as f:
        md_text = f.read()

    md_conv = _md.Markdown(extensions=["fenced_code", "tables", "sane_lists"])
    html_content = md_conv.convert(md_text)

    parser = _MdHTMLParser(styles_map, link_c)
    parser.feed(html_content)
    story = parser.get_story()

    def on_page(canvas, doc):
        canvas.saveState()
        canvas.setFillColor(bg_c)
        canvas.rect(0, 0, page_w, page_h, fill=1, stroke=0)
        if show_header:
            canvas.setFillColor(hr_c)
            canvas.rect(0, page_h - header_h, page_w, header_h, fill=1, stroke=0)
            canvas.setFillColor(text_c)
            canvas.setFont("Helvetica-Bold", 8)
            canvas.drawString(margin, page_h - 0.27*inch, os.path.basename(md_file))
            canvas.setFont("Helvetica", 8)
            canvas.drawRightString(page_w - margin, page_h - 0.27*inch, f"Page {doc.page}")
        canvas.restoreState()

    doc = SimpleDocTemplate(
        output_file, pagesize=page_size,
        leftMargin=margin, rightMargin=margin,
        topMargin=margin + header_h, bottomMargin=margin,
        title=os.path.basename(md_file),
    )
    doc.build(story, onFirstPage=on_page, onLaterPages=on_page)

    if progress_callback:
        progress_callback(100)

def _hex_to_color(h: str) -> Color:
    h = h.lstrip("#")
    return Color(int(h[0:2], 16) / 255, int(h[2:4], 16) / 255, int(h[4:6], 16) / 255)


def _token_color(ttype, theme: dict) -> str:
    """Walk the Pygments token hierarchy upward to find the best color."""
    t = ttype
    while t:
        if t in theme:
            return theme[t]
        parent = t.parent if t.parent is not t else None
        if parent is None or parent == t:
            break
        t = parent
    return theme.get("default", "#FFFFFF")


def generate_pdf(
    python_file: str,
    output_file: str,
    theme_name: str,
    page_size_name: str,
    orientation: str,
    font_size: int,
    show_line_numbers: bool,
    show_header: bool,
    progress_callback=None,
):
    theme = THEMES[theme_name]
    base_size = PAGE_SIZES[page_size_name]

    if orientation == "Landscape":
        from reportlab.lib.pagesizes import landscape
        page_w, page_h = landscape(base_size)
    else:
        page_w, page_h = base_size

    margin = 0.55 * inch
    line_height = font_size * 1.45
    char_w = font_size * 0.601  # Courier character width ratio

    with open(python_file, "r", encoding="utf-8", errors="replace") as f:
        source = f.read()

    # Tokenize and split into per-line token lists
    raw_tokens = list(lex(source, PythonLexer()))
    lines: list[list[tuple]] = [[]]
    for ttype, value in raw_tokens:
        parts = value.split("\n")
        for i, part in enumerate(parts):
            if i > 0:
                lines.append([])
            if part:
                lines[-1].append((ttype, part))

    total_lines = len(lines)
    num_digits = len(str(total_lines))
    gutter_w = (num_digits * char_w + 18) if show_line_numbers else 0
    header_h = 26 if show_header else 0

    content_x = margin + gutter_w
    content_top = page_h - margin - header_h
    content_bottom = margin + 4

    c = rl_canvas.Canvas(output_file, pagesize=(page_w, page_h))
    c.setTitle(os.path.basename(python_file))
    c.setAuthor("Python → PDF Converter")

    bg_c       = _hex_to_color(theme["bg"])
    gutter_bg_c = _hex_to_color(theme["gutter_bg"])
    gutter_fg_c = _hex_to_color(theme["gutter_fg"])
    header_bg_c = _hex_to_color(theme["header_bg"])
    header_fg_c = _hex_to_color(theme["header_fg"])

    page_num = 1

    def draw_background():
        c.setFillColor(bg_c)
        c.rect(0, 0, page_w, page_h, fill=1, stroke=0)

        if show_line_numbers and gutter_w > 0:
            c.setFillColor(gutter_bg_c)
            c.rect(margin, margin, gutter_w - 4, page_h - 2 * margin - header_h, fill=1, stroke=0)
            # subtle separator
            c.setStrokeColor(gutter_fg_c)
            c.setLineWidth(0.3)
            c.line(margin + gutter_w - 4, margin,
                   margin + gutter_w - 4, page_h - margin - header_h)

        if show_header:
            c.setFillColor(header_bg_c)
            c.rect(0, page_h - header_h, page_w, header_h, fill=1, stroke=0)
            c.setStrokeColor(gutter_fg_c)
            c.setLineWidth(0.5)
            c.line(0, page_h - header_h, page_w, page_h - header_h)

            c.setFillColor(header_fg_c)
            c.setFont("Courier-Bold", 9)
            c.drawString(margin, page_h - header_h + 9, os.path.basename(python_file))
            c.setFont("Courier", 9)
            c.drawCentredString(page_w / 2, page_h - header_h + 9, theme_name)
            c.drawRightString(page_w - margin, page_h - header_h + 9, f"Page {page_num}")

    draw_background()
    y = content_top - line_height

    for line_idx, line_tokens in enumerate(lines):
        if progress_callback and line_idx % 40 == 0:
            progress_callback(line_idx / total_lines * 100)

        if y < content_bottom:
            c.showPage()
            page_num += 1
            draw_background()
            y = content_top - line_height

        # Gutter – line number
        if show_line_numbers and gutter_w > 0:
            c.setFillColor(gutter_fg_c)
            c.setFont("Courier", font_size)
            c.drawRightString(margin + gutter_w - 8, y, str(line_idx + 1))

        # Tokens
        x = content_x
        for ttype, text in line_tokens:
            if not text:
                continue

            text = text.replace("\t", "    ")

            color_hex = _token_color(ttype, theme)
            c.setFillColor(_hex_to_color(color_hex))

            is_bold = ttype in Token.Keyword
            c.setFont("Courier-Bold" if is_bold else "Courier", font_size)

            # Clip text to page width
            avail_chars = max(0, int((page_w - margin - x) / char_w))
            if len(text) > avail_chars:
                text = text[:avail_chars]
            if not text:
                break

            c.drawString(x, y, text)
            x += len(text) * char_w

        y -= line_height

    c.save()
    if progress_callback:
        progress_callback(100)


# ──────────────────────────────────────────────────────────────────────────────
# GUI
# ──────────────────────────────────────────────────────────────────────────────

APP_BG    = "#1A1A2E"
PANEL_BG  = "#16213E"
ACCENT    = "#0F3460"
BTN_RED   = "#E94560"
FG        = "#EAEAEA"
FG_DIM    = "#888888"
BORDER    = "#2A3A5C"


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Python → PDF Converter")
        self.resizable(False, False)
        self.configure(bg=APP_BG)
        self._theme_frames: dict[str, tk.Frame] = {}
        self._setup_style()
        self._build_ui()

    # ── style ──────────────────────────────────────────────────────────────

    def _setup_style(self):
        s = ttk.Style(self)
        s.theme_use("clam")

        s.configure("TFrame",        background=APP_BG)
        s.configure("Panel.TFrame",  background=PANEL_BG)

        s.configure("TLabel",        background=APP_BG,   foreground=FG,     font=("Segoe UI", 10))
        s.configure("Dim.TLabel",    background=APP_BG,   foreground=FG_DIM, font=("Segoe UI", 9))
        s.configure("H1.TLabel",     background=APP_BG,   foreground=FG,     font=("Segoe UI", 18, "bold"))
        s.configure("Panel.TLabel",  background=PANEL_BG, foreground=FG,     font=("Segoe UI", 10))
        s.configure("PHead.TLabel",  background=PANEL_BG, foreground=FG,     font=("Segoe UI", 10, "bold"))

        s.configure("TCombobox",
                    fieldbackground=ACCENT, background=PANEL_BG,
                    foreground=FG, selectbackground=ACCENT, selectforeground=FG)
        s.map("TCombobox", fieldbackground=[("readonly", ACCENT)])

        s.configure("TCheckbutton", background=PANEL_BG, foreground=FG, font=("Segoe UI", 10))
        s.map("TCheckbutton", background=[("active", PANEL_BG)], foreground=[("active", FG)])

        s.configure("Primary.TButton",
                    background=BTN_RED, foreground="white",
                    font=("Segoe UI", 11, "bold"), padding=(22, 10),
                    relief="flat", borderwidth=0)
        s.map("Primary.TButton",
              background=[("active", "#C73652"), ("disabled", "#555")])

        s.configure("Sec.TButton",
                    background=ACCENT, foreground=FG,
                    font=("Segoe UI", 9), padding=(10, 5), relief="flat")
        s.map("Sec.TButton", background=[("active", "#1A4A7A")])

        s.configure("TProgressbar", troughcolor=ACCENT, background=BTN_RED, thickness=6)

    # ── layout builders ────────────────────────────────────────────────────

    def _build_ui(self):
        # Title bar
        top = ttk.Frame(self)
        top.pack(fill="x", padx=24, pady=(18, 4))
        ttk.Label(top, text="Code & Markdown → PDF", style="H1.TLabel").pack(anchor="w")
        ttk.Label(top, text="Convert .py and .md files to styled PDFs",
                  style="Dim.TLabel").pack(anchor="w")

        # Two-column body
        body = ttk.Frame(self)
        body.pack(fill="both", expand=True, padx=24, pady=8)

        left = ttk.Frame(body)
        left.pack(side="left", fill="both", expand=True, padx=(0, 10))
        right = ttk.Frame(body)
        right.pack(side="right", fill="both", expand=True, padx=(10, 0))

        self._section(left,  "Files",            self._files_content)
        self._section(left,  "Theme",            self._theme_content)

        self._section(right, "Page Setup",       self._page_content)
        self._section(right, "Font Size",        self._font_content)
        self._section(right, "Options",          self._options_content)

        # Progress + status
        foot = ttk.Frame(self)
        foot.pack(fill="x", padx=24, pady=(4, 0))
        self.progress_var = tk.DoubleVar()
        ttk.Progressbar(foot, variable=self.progress_var, maximum=100).pack(fill="x")
        self.status_var = tk.StringVar(value="Ready")
        ttk.Label(foot, textvariable=self.status_var, style="Dim.TLabel").pack(anchor="w", pady=2)

        # Action row
        actions = ttk.Frame(self)
        actions.pack(fill="x", padx=24, pady=(8, 18))
        self.convert_btn = ttk.Button(actions, text="⚡  Convert to PDF",
                                      style="Primary.TButton", command=self._start_convert)
        self.convert_btn.pack(side="right")
        ttk.Button(actions, text="Preview Theme", style="Sec.TButton",
                   command=self._show_preview).pack(side="right", padx=(0, 8))

    def _section(self, parent, title: str, builder):
        f = tk.Frame(parent, bg=PANEL_BG, bd=0, relief="flat")
        f.pack(fill="x", pady=(0, 10))
        # inner padding
        inner = tk.Frame(f, bg=PANEL_BG)
        inner.pack(fill="x", padx=14, pady=10)
        ttk.Label(inner, text=title, style="PHead.TLabel").pack(anchor="w", pady=(0, 8))
        builder(inner)

    # ── section contents ───────────────────────────────────────────────────

    def _files_content(self, p):
        self.input_var  = tk.StringVar()
        self.output_var = tk.StringVar()

        for label, var, cmd in [
            ("Input .py",  self.input_var,  self._browse_input),
            ("Output PDF", self.output_var, self._browse_output),
        ]:
            row = tk.Frame(p, bg=PANEL_BG)
            row.pack(fill="x", pady=3)
            tk.Label(row, text=label + ":", bg=PANEL_BG, fg=FG,
                     font=("Segoe UI", 9), width=11, anchor="w").pack(side="left")
            tk.Entry(row, textvariable=var, width=30,
                     bg=ACCENT, fg=FG, insertbackground=FG,
                     relief="flat", font=("Segoe UI", 9), bd=4).pack(side="left", padx=(4, 4))
            ttk.Button(row, text="Browse", style="Sec.TButton", command=cmd).pack(side="left")

    def _theme_content(self, p):
        self.theme_var = tk.StringVar(value="VSCode Dark+")
        grid = tk.Frame(p, bg=PANEL_BG)
        grid.pack(fill="x")

        for i, (name, theme) in enumerate(THEMES.items()):
            col, row = i % 2, i // 2
            cell = tk.Frame(grid, bg=theme["bg"], cursor="hand2",
                            highlightthickness=2, highlightbackground=PANEL_BG)
            cell.grid(row=row, column=col, padx=3, pady=3, sticky="ew")
            grid.columnconfigure(col, weight=1)

            # Color dots preview
            dots = tk.Frame(cell, bg=theme["bg"])
            dots.pack(side="left", padx=6, pady=5)
            sample_colors = [
                theme.get(Token.Keyword,        theme["default"]),
                theme.get(Token.Literal.String, theme["default"]),
                theme.get(Token.Comment,        theme["default"]),
                theme.get(Token.Name.Function,  theme["default"]),
                theme.get(Token.Literal.Number, theme["default"]),
            ]
            for sc in sample_colors:
                tk.Label(dots, text="●", fg=sc, bg=theme["bg"],
                         font=("Segoe UI", 7)).pack(side="left")

            lbl = tk.Label(cell, text=name, bg=theme["bg"], fg=theme["default"],
                           font=("Segoe UI", 8, "bold"), pady=2, padx=4)
            lbl.pack(side="left")

            def _select(n=name):
                self.theme_var.set(n)
                self._highlight_theme(n)

            for w in (cell, dots, lbl):
                w.bind("<Button-1>", lambda e, fn=_select: fn())

            self._theme_frames[name] = cell

        self._highlight_theme("VSCode Dark+")

    def _highlight_theme(self, selected: str):
        for name, cell in self._theme_frames.items():
            cell.config(highlightbackground=BTN_RED if name == selected else PANEL_BG,
                        highlightthickness=2)

    def _page_content(self, p):
        # Page size
        row = tk.Frame(p, bg=PANEL_BG)
        row.pack(fill="x", pady=3)
        tk.Label(row, text="Size:", bg=PANEL_BG, fg=FG,
                 font=("Segoe UI", 9), width=12, anchor="w").pack(side="left")
        self.page_size_var = tk.StringVar(value='A4 (210×297mm)')
        ttk.Combobox(row, textvariable=self.page_size_var,
                     values=list(PAGE_SIZES.keys()), state="readonly",
                     width=22).pack(side="left")

        # Orientation
        row2 = tk.Frame(p, bg=PANEL_BG)
        row2.pack(fill="x", pady=3)
        tk.Label(row2, text="Orientation:", bg=PANEL_BG, fg=FG,
                 font=("Segoe UI", 9), width=12, anchor="w").pack(side="left")
        self.orientation_var = tk.StringVar(value="Portrait")
        for val in ("Portrait", "Landscape"):
            tk.Radiobutton(row2, text=val, variable=self.orientation_var,
                           value=val, bg=PANEL_BG, fg=FG,
                           selectcolor=ACCENT, activebackground=PANEL_BG,
                           activeforeground=FG, font=("Segoe UI", 9)).pack(side="left", padx=6)

    def _font_content(self, p):
        row = tk.Frame(p, bg=PANEL_BG)
        row.pack(fill="x")
        self.font_size_var = tk.IntVar(value=9)
        self._size_lbl = tk.Label(row, text=" 9 pt", bg=PANEL_BG, fg=FG,
                                   font=("Courier New", 10, "bold"), width=5)
        self._size_lbl.pack(side="right")
        tk.Scale(row, from_=6, to=16, orient="horizontal",
                 variable=self.font_size_var, length=200,
                 bg=PANEL_BG, fg=FG, troughcolor=ACCENT,
                 highlightthickness=0, showvalue=False,
                 command=lambda v: self._size_lbl.config(text=f"{int(float(v)):2d} pt")
                 ).pack(side="left", fill="x", expand=True)

    def _options_content(self, p):
        self.show_line_nums = tk.BooleanVar(value=True)
        self.show_header    = tk.BooleanVar(value=True)
        for text, var in [
            ("Show line numbers",            self.show_line_nums),
            ("Show filename / page header",  self.show_header),
        ]:
            ttk.Checkbutton(p, text=text, variable=var).pack(anchor="w", pady=1)

    # ── file browsing ──────────────────────────────────────────────────────

    def _browse_input(self):
        path = filedialog.askopenfilename(
            title="Select file",
            filetypes=[
                ("Supported files", "*.py *.pyw *.md *.markdown"),
                ("Python files", "*.py *.pyw"),
                ("Markdown files", "*.md *.markdown"),
                ("All files", "*.*"),
            ],
        )
        if path:
            self.input_var.set(path)
            if not self.output_var.get():
                self.output_var.set(os.path.splitext(path)[0] + ".pdf")

    def _browse_output(self):
        path = filedialog.asksaveasfilename(
            title="Save PDF as",
            defaultextension=".pdf",
            filetypes=[("PDF files", "*.pdf")],
        )
        if path:
            self.output_var.set(path)

    # ── theme preview ──────────────────────────────────────────────────────

    def _show_preview(self):
        theme_name = self.theme_var.get()
        theme = THEMES[theme_name]

        sample = '''\
# VSCode-style Python theme preview
import os
from pathlib import Path
from typing import Optional

CONSTANT = 3.14159


class FileConverter:
    """Converts Python files to styled PDFs."""

    VERSION = "2.0.0"

    def __init__(self, theme: str = "VSCode Dark+"):
        self.theme = theme
        self._pages: list[str] = []

    def convert(self, path: str) -> Optional[bool]:
        """Convert file at path to PDF and return success."""
        if not os.path.exists(path):
            raise FileNotFoundError(f"Missing: {path}")

        lines = Path(path).read_text(encoding="utf-8").splitlines()
        for i, line in enumerate(lines, 1):
            self._pages.append(f"{i:4d}  {line}")

        return True  # success


converter = FileConverter(theme="VSCode Dark+")
result = converter.convert("my_script.py")
print(f"Done: {result}")
'''

        win = tk.Toplevel(self)
        win.title(f"Theme Preview — {theme_name}")
        win.configure(bg=theme["bg"])
        win.resizable(True, True)

        # header bar
        hdr = tk.Frame(win, bg=theme["header_bg"], height=26)
        hdr.pack(fill="x")
        tk.Label(hdr, text=f"  preview.py   —   {theme_name}",
                 bg=theme["header_bg"], fg=theme["header_fg"],
                 font=("Segoe UI", 9)).pack(side="left", pady=4)

        txt = tk.Text(win, bg=theme["bg"], fg=theme["default"],
                      font=("Courier New", 10), width=62, height=30,
                      relief="flat", insertbackground=theme["default"],
                      selectbackground="#264F78", padx=10, pady=8,
                      wrap="none")
        txt.pack(fill="both", expand=True, padx=1, pady=1)

        # Syntax-highlight the sample
        raw = list(lex(sample, PythonLexer()))
        for ttype, value in raw:
            color = _token_color(ttype, theme)
            tag = f"c{color.replace('#','')}"
            bold = ttype in Token.Keyword
            txt.tag_configure(tag, foreground=color,
                              font=("Courier New", 10, "bold" if bold else "normal"))
            txt.insert("end", value, tag)

        txt.config(state="disabled")

    # ── conversion ─────────────────────────────────────────────────────────

    def _start_convert(self):
        src = self.input_var.get().strip()
        dst = self.output_var.get().strip()

        if not src:
            messagebox.showerror("Missing input", "Please select a .py or .md file.")
            return
        if not os.path.isfile(src):
            messagebox.showerror("Not found", f"File does not exist:\n{src}")
            return
        if not dst:
            messagebox.showerror("Missing output", "Please specify an output PDF path.")
            return

        self.convert_btn.config(state="disabled")
        self.progress_var.set(0)
        self.status_var.set("Starting…")

        ext = os.path.splitext(src)[1].lower()
        is_md = ext in (".md", ".markdown")

        def _run():
            try:
                if is_md:
                    generate_md_pdf(
                        md_file=src,
                        output_file=dst,
                        theme_name=self.theme_var.get(),
                        page_size_name=self.page_size_var.get(),
                        orientation=self.orientation_var.get(),
                        font_size=self.font_size_var.get(),
                        show_header=self.show_header.get(),
                        progress_callback=self._update_progress,
                    )
                else:
                    generate_pdf(
                        python_file=src,
                        output_file=dst,
                        theme_name=self.theme_var.get(),
                        page_size_name=self.page_size_var.get(),
                        orientation=self.orientation_var.get(),
                        font_size=self.font_size_var.get(),
                        show_line_numbers=self.show_line_nums.get(),
                        show_header=self.show_header.get(),
                        progress_callback=self._update_progress,
                    )
                self.after(0, self._on_success, dst)
            except Exception as exc:
                self.after(0, self._on_error, str(exc))

        threading.Thread(target=_run, daemon=True).start()

    def _update_progress(self, pct: float):
        self.progress_var.set(pct)
        self.status_var.set(f"Converting… {pct:.0f}%")

    def _on_success(self, path: str):
        self.convert_btn.config(state="normal")
        self.progress_var.set(100)
        self.status_var.set(f"Done! → {os.path.basename(path)}")
        if messagebox.askyesno("Success",
                                f"PDF created:\n\n{path}\n\nOpen it now?"):
            os.startfile(path)

    def _on_error(self, msg: str):
        self.convert_btn.config(state="normal")
        self.progress_var.set(0)
        self.status_var.set("Error — see dialog")
        messagebox.showerror("Conversion failed", msg)


# ──────────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    app = App()
    app.mainloop()
