from __future__ import annotations

"""Pure‑Python Markdown → **tree** parser

This replaces the previous flat‑list model with a hierarchical tree that
reflects heading structure::

    Document
    ├── Section(level=1, title="Title")
    │   ├── Paragraph(...)
    │   └── Section(level=2, title="Sub")
    │       └── CodeBlock(...)
    └── Section(level=1, title="Another top‑level")

Only standard library modules are used.  Supported blocks:

* ATX headings   (#, ## …)               → `Section`
* Paragraphs                             → `Paragraph`
* Fenced code blocks (```)               → `CodeBlock`
* Unordered and ordered lists            → `ListBlock` / `ListItem`
* GitHub‑style tables (| col | col |)    → `Table`

Add new block types by extending `_is_*` / `_parse_*` helpers and the
`_other_dispatch` table.
"""

from dataclasses import dataclass
from typing import List, Union, Any

# ---------------------------------------------------------------------------
# Element model -------------------------------------------------------------
# ---------------------------------------------------------------------------


class MarkdownElement:
    def to_dict(self) -> dict[str, Any]:
        return {
            "type": self.__class__.__name__.lower(),
            **{
                k: (v if not isinstance(v, list) else [i.to_dict() for i in v])
                for k, v in self.__dict__.items()
                if not k.startswith("_")
            },
        }

    def __repr__(self) -> str:  # pragma: no cover
        return f"<{self.__class__.__name__} {self.__dict__}>"


@dataclass
class Paragraph(MarkdownElement):
    text: str


@dataclass
class CodeBlock(MarkdownElement):
    language: str | None
    code: str


@dataclass
class ListItem(MarkdownElement):
    text: str


@dataclass
class ListBlock(MarkdownElement):
    ordered: bool
    items: List[ListItem]


@dataclass
class Table(MarkdownElement):
    headers: List[str]
    rows: List[List[str]]


# Forward reference for recursive type --------------------------------------
Block = Union[Paragraph, CodeBlock, ListBlock, Table, "Section"]


@dataclass
class Section(MarkdownElement):
    level: int
    title: str
    children: List[Block]


@dataclass
class Document(MarkdownElement):
    children: List[Block]


# ---------------------------------------------------------------------------
# Parser --------------------------------------------------------------------
# ---------------------------------------------------------------------------


class MarkdownParser:
    """No‑dependency Markdown → tree parser.

    Instantiate once and call :py:meth:`parse` repeatedly.
    """

    _UL_MARKERS = {"-", "*", "+"}

    # Public API -----------------------------------------------------------

    def parse(self, markdown_text: str) -> Document:
        """Return a :class:`Document` representing *markdown_text*."""
        self._lines = (
            markdown_text.replace("\r\n", "\n").replace("\r", "\n").split("\n")
        )
        self._len = len(self._lines)
        self._pos = 0

        root = Section(level=0, title="", children=[])
        stack: List[Section] = [root]

        while self._pos < self._len:
            line = self._current_line

            if self._is_heading(line):
                sec = self._parse_heading()
                # Find parent level
                while stack and stack[-1].level >= sec.level:
                    stack.pop()
                stack[-1].children.append(sec)
                stack.append(sec)
                continue

            block = self._parse_other()
            if block is not None:
                stack[-1].children.append(block)
            else:  # blank or unknown line
                self._advance()

        return Document(children=root.children)

    # ------------------------------------------------------------------
    # Line helpers ------------------------------------------------------
    # ------------------------------------------------------------------

    @property
    def _current_line(self) -> str:
        return self._lines[self._pos]

    def _advance(self, n: int = 1) -> None:
        self._pos = min(self._pos + n, self._len)

    # ------------------------------------------------------------------
    # Heading (handled separately) -------------------------------------
    # ------------------------------------------------------------------

    def _is_heading(self, line: str) -> bool:
        stripped = line.lstrip()
        return stripped.startswith("#") and stripped.rstrip("#").strip() != ""

    def _parse_heading(self) -> Section:
        line = self._current_line.lstrip()
        level = len(line) - len(line.lstrip("#"))
        title = line[level:].strip().rstrip("#").strip()
        self._advance()
        return Section(level=level, title=title, children=[])

    # ------------------------------------------------------------------
    # Other blocks (dispatch table) ------------------------------------
    # ------------------------------------------------------------------

    def _parse_other(self) -> Block | None:
        # Order matters
        for pred, parse_fn in self._other_dispatch:
            if pred(self._current_line):
                return parse_fn()
        return None  # blank or unsupported line

    # Predicate + parse function tables --------------------------------

    def __init__(self):
        # Build dispatch once
        self._other_dispatch = [
            (self._is_fence, self._parse_fenced_code),
            (self._is_table_row, self._parse_table),
            (self._is_list_item, self._parse_list),
            (self._is_paragraph, self._parse_paragraph),
        ]

    # 1. Fenced code block ---------------------------------------------
    def _is_fence(self, line: str) -> bool:
        return line.lstrip().startswith("```")

    def _parse_fenced_code(self) -> CodeBlock:
        fence = self._current_line.lstrip()
        language = fence[3:].strip() or None
        self._advance()
        code_lines: List[str] = []
        while self._pos < self._len and not self._current_line.lstrip().startswith(
            "```"
        ):
            code_lines.append(self._current_line)
            self._advance()
        self._advance()  # closing fence
        return CodeBlock(language=language, code="\n".join(code_lines))

    # 2. Tables ---------------------------------------------------------
    def _is_table_row(self, line: str) -> bool:
        l = line.strip()
        return l.startswith("|") and l.endswith("|") and "|" in l[1:-1]

    def _parse_table(self) -> Table:
        header = self._split_table_row(self._current_line)
        self._advance()
        if self._pos < self._len and set(
            self._current_line.replace("|", "").strip()
        ) <= {"-", ":"}:
            self._advance()
        rows: List[List[str]] = []
        while self._pos < self._len and self._is_table_row(self._current_line):
            rows.append(self._split_table_row(self._current_line))
            self._advance()
        return Table(headers=header, rows=rows)

    @staticmethod
    def _split_table_row(line: str) -> List[str]:
        return [cell.strip() for cell in line.strip().strip("|").split("|")]

    # 3. Lists ----------------------------------------------------------
    def _is_list_item(self, line: str) -> bool:
        stripped = line.lstrip()
        if not stripped:
            return False
        first, rest = stripped[0], stripped[1:]
        if first in self._UL_MARKERS and rest.startswith(" "):
            return True
        if first.isdigit():
            return rest.startswith(". ")
        return False

    def _parse_list(self) -> ListBlock:
        ordered = False
        items: List[ListItem] = []
        while self._pos < self._len and self._is_list_item(self._current_line):
            line = self._current_line.lstrip()
            marker, content = line.split(" ", 1)
            if marker[0].isdigit():
                ordered = True
            items.append(ListItem(text=content.strip()))
            self._advance()
        return ListBlock(ordered=ordered, items=items)

    # 4. Paragraph ------------------------------------------------------
    def _is_paragraph(self, line: str) -> bool:
        return line.strip() != ""

    def _parse_paragraph(self) -> Paragraph:
        lines: List[str] = []
        while self._pos < self._len and self._current_line.strip() != "":
            lines.append(self._current_line.strip())
            self._advance()
        # consume blank lines
        while self._pos < self._len and self._current_line.strip() == "":
            self._advance()
        return Paragraph(text=" ".join(lines))


def parse_markdown(markdown_text: str) -> Document:
    """Parse *markdown_text* and return a :class:`Document`."""
    parser = MarkdownParser()
    return parser.parse(markdown_text)
