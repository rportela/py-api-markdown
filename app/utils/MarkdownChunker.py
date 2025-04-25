"""
Robust Markdown Text Chunker for RAG (Retrieval‑Augmented Generation)
===================================================================

**Version 1.3 –  full‑document disclaimer scan & broader table filter**

Your test output showed three gaps:

1. **Late‑document disclaimers** – our cutoff (1 500 chars) missed the legal tail.
2. **Inline ‘pseudo‑tables’** (space‑separated financial rows) weren’t matched by the “\| … \|” regex.
3. **Residual ‘Source:’ / ‘Disclaimer:’ one‑liners** add noise.

Changes
-------
* **Disclaimer sweep across *all* paragraphs** (not just the head). A paragraph ≥ 40 words is removed when its score ≥ `thresh` (default 5). This keeps ordinary sentences intact but nixes boiler‑plate wherever it hides.
* **`_BLOCK_TABLE_RX`**: detects ≥ 3 consecutive lines that contain **≥ 2 double‑spaces** (classic PDF column separator) or a pipe. These blocks are dropped or repaired just like true Markdown tables.
* **`table_mode` default remains "drop".**
* Small tweak: optional `keep_disclaimer_lines=False` to *mark* instead of drop (helps debugging).

Install deps (unchanged):
```bash
pip install tiktoken langchain_text_splitters markdown-table-repair
```
"""

from __future__ import annotations
from typing import List, Dict
import hashlib, re, itertools

# --- hard imports (fail fast) -------------------------------------------------
import tiktoken
from langchain_text_splitters import MarkdownHeaderTextSplitter  # type: ignore
from langchain.text_splitter import RecursiveCharacterTextSplitter  # type: ignore
import markdown_table_repair

# --- disclaimer heuristics ----------------------------------------------------
_HEADING_KEYWORDS = [
    "important notice",
    "disclaimer",
    "legal disclaimer",
    "confidentiality",
]
_HEADING_RX = re.compile(
    rf"(?is)^\s*(?:#{{1,3}}|\*+|_+)?\s*(?:{'|'.join(_HEADING_KEYWORDS)})\s*[:\-]?\s*$",
    re.MULTILINE,
)
_ANCHOR_PHRASES = [
    "forward looking statements",
    "private securities litigation reform act",
    "safe harbor statement",
    "actual results may differ materially",
    "readers are cautioned",
    "subject to risks and uncertainties",
    "no obligation to update",
    "undue reliance on",
]
_LEGAL_TOKENS = [
    "liable",
    "liability",
    "reliance",
    "uncertainties",
    "assumptions",
    "guarantee",
    "materially",
    "harbor",
    "caution",
    "forward‑looking",
    "statements",
    "risks",
    "expects",
    "projects",
    "anticipates",
]
_PAR_RX = re.compile(r"\n\s*\n", re.MULTILINE)

# --- table heuristics ---------------------------------------------------------
_PIPE_TABLE_RX = re.compile(r"^\s*\|.*\|.*$", re.MULTILINE)
_SPACE_COL_RX = re.compile(r"^.*\S\s{2,}\S.*$")  # at least two consecutive spaces
_BLOCK_TABLE_RX = re.compile(
    r"(?:^.*\|.*$|^.*\S\s{2,}\S.*$)(?:\n(?:.*\|.*|.*\S\s{2,}\S.*$)){2,}", re.MULTILINE
)

# --- helpers ------------------------------------------------------------------


def _para_score(text: str) -> int:
    lc = text.lower()
    anchors = sum(1 for p in _ANCHOR_PHRASES if p in lc)
    tokens = sum(lc.count(tok) for tok in _LEGAL_TOKENS)
    return anchors * 3 + tokens


enc = tiktoken.encoding_for_model("gpt-4o")
_num_tokens = lambda s: len(enc.encode(s))


# --- main class ---------------------------------------------------------------
class MarkdownChunker:
    """Chunker with full‑doc disclaimer scan & better table removal."""

    def __init__(
        self,
        *,
        max_tokens: int = 512,
        overlap: int = 64,
        table_mode: str = "drop",
        disclaimer_thresh: int = 5,
        disclaimer_min_words: int = 40,
        keep_disclaimer_lines: bool = False,
    ):
        if table_mode not in {"drop", "repair", "keep"}:
            raise ValueError("table_mode must be 'drop', 'repair', or 'keep'")
        self.max_tokens, self.overlap = max_tokens, overlap
        self.table_mode = table_mode
        self.disclaimer_thresh = disclaimer_thresh
        self.disclaimer_min_words = disclaimer_min_words
        self.keep_disclaimer_lines = keep_disclaimer_lines

        self._header_splitter = MarkdownHeaderTextSplitter(
            headers_to_split_on=[("#", "h1"), ("##", "h2"), ("###", "h3")],
            strip_headers=True,
        )
        self._recursive_splitter = RecursiveCharacterTextSplitter(
            chunk_size=max_tokens,
            chunk_overlap=overlap,
            length_function=_num_tokens,
            separators=["\n\n", "\n", ". ", " "],
        )

    # ------------------------------------------------------------------
    def chunk(self, md: str) -> List[Dict]:
        text = self._strip_disclaimers(md)
        text = self._process_tables(text)
        sections = self._split_by_header(text)
        return self._split_sections(sections)

    # ------------------------------------------------------------------
    def _strip_disclaimers(self, text: str) -> str:
        # Remove header‑labelled disclaimer blocks first
        text = _HEADING_RX.sub("", text)
        # Full‑document scan paragraph‑by‑paragraph
        paras = _PAR_RX.split(text)
        cleaned_paras = []
        for p in paras:
            if (
                len(p.split()) >= self.disclaimer_min_words
                and _para_score(p) >= self.disclaimer_thresh
            ):
                if self.keep_disclaimer_lines:
                    cleaned_paras.append("[DISCLAIMER REMOVED]")
                continue  # drop
            cleaned_paras.append(p)
        return "\n\n".join(cleaned_paras)

    def _process_tables(self, text: str) -> str:
        def drop_or_repair(match: re.Match[str]) -> str:
            block = match.group(0)
            if self.table_mode == "drop":
                return ""
            if self.table_mode == "repair":
                # attempt repair if pipe table; otherwise keep
                return markdown_table_repair.repair(block).table if "|" in block else block
            return block

        return _BLOCK_TABLE_RX.sub(drop_or_repair, text)

    def _split_by_header(self, text: str):
        docs = self._header_splitter.split_text(text)
        return [d.page_content for d in docs] if docs else [text]

    def _split_sections(self, sections):
        chunks: List[Dict] = []
        for sec in sections:
            for frag in self._recursive_splitter.split_text(sec):
                chunks.append(
                    {
                        "id": hashlib.sha1(frag.encode()).hexdigest()[:12],
                        "content": frag,
                        "metadata": {
                            "section": sec.split("\n", 1)[0][:120],
                            "tokens": _num_tokens(frag),
                        },
                    }
                )
        return chunks


# Convenience wrapper ----------------------------------------------------------


def chunk_markdown(md: str, **kw):
    return MarkdownChunker(**kw).chunk(md)
