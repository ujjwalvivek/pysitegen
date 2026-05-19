from __future__ import annotations

import re
from dataclasses import dataclass
from html import escape
from pathlib import Path
from typing import Any, cast

from . import components as _components
from .components import Node
from .elements import a, h1, h2, h3, li, p, tag, ul


PYTHON_KEYWORDS = {
    "False",
    "None",
    "True",
    "and",
    "as",
    "assert",
    "async",
    "await",
    "break",
    "class",
    "continue",
    "def",
    "del",
    "elif",
    "else",
    "except",
    "finally",
    "for",
    "from",
    "global",
    "if",
    "import",
    "in",
    "is",
    "lambda",
    "nonlocal",
    "not",
    "or",
    "pass",
    "raise",
    "return",
    "try",
    "while",
    "with",
    "yield",
}
PYTHON_BUILTINS = {
    "Path",
    "False",
    "None",
    "True",
    "dict",
    "float",
    "int",
    "list",
    "set",
    "str",
    "tuple",
}
BASH_COMMANDS = {
    "cd",
    "pip",
    "pysitegen",
    "python",
}
PYTHON_TOKEN_RE = re.compile(
    r"(?P<comment>#.*$)"
    r"|(?P<string>\"(?:\\.|[^\"\\])*\"|'(?:\\.|[^'\\])*')"
    r"|(?P<number>\b\d+(?:\.\d+)?\b)"
    r"|(?P<decorator>@[A-Za-z_][A-Za-z0-9_]*)"
    r"|(?P<name>\b[A-Za-z_][A-Za-z0-9_]*\b)"
    r"|(?P<operator>[()[\]{}.,:=+\-*/%<>!|&]+)"
)
BASH_TOKEN_RE = re.compile(
    r"(?P<comment>#.*$)"
    r"|(?P<string>\"(?:\\.|[^\"\\])*\"|'(?:\\.|[^'\\])*')"
    r"|(?P<option>(?<!\S)--?[A-Za-z0-9][A-Za-z0-9_-]*)"
    r"|(?P<variable>\$[A-Za-z_][A-Za-z0-9_]*)"
    r"|(?P<word>[A-Za-z_./][A-Za-z0-9_./-]*)"
    r"|(?P<operator>[|&;=<>]+)"
)


@dataclass(frozen=True)
class Heading:
    level: int
    text: str
    slug: str


@dataclass(frozen=True)
class MarkdownDocument:
    nodes: list[Node]
    headings: list[Heading]


def markdown_file(path: str | Path) -> MarkdownDocument:
    return markdown_text(Path(path).read_text(encoding="utf-8"))


def markdown_text(text: str) -> MarkdownDocument:
    parser = MarkdownParser(text)
    return parser.parse()


def markdown_toc(
    document: MarkdownDocument,
    title: str = "On this page",
    collapsible: bool = False,
    open: bool = False,
) -> Node:
    toc_list = markdown_toc_list(document)
    if collapsible:
        return tag(
            "aside",
            p(title, class_="eyebrow docs-toc-desktop-title"),
            markdown_toc_list(document, class_name="docs-toc-list docs-toc-desktop-list"),
            tag(
                "details",
                tag("summary", title, class_="docs-toc-summary"),
                markdown_toc_list(document, class_name="docs-toc-list docs-toc-mobile-list"),
                class_="docs-toc-details",
                open=open,
            ),
            class_="docs-toc collapsible",
        )

    return tag(
        "aside",
        p(title, class_="eyebrow"),
        toc_list,
        class_="docs-toc",
    )


def markdown_toc_list(
    document: MarkdownDocument,
    class_name: str = "docs-toc-list",
) -> Node:
    items = [
        li(a(heading.text, href=f"#{heading.slug}", class_=f"toc-link level-{heading.level}"))
        for heading in document.headings
        if heading.level in {2, 3}
    ]
    return ul(items, class_=class_name)


class MarkdownParser:
    def __init__(self, text: str) -> None:
        self.lines = text.splitlines()
        self.index = 0
        self.nodes: list[Node] = []
        self.headings: list[Heading] = []
        self.slug_counts: dict[str, int] = {}

    def parse(self) -> MarkdownDocument:
        while self.index < len(self.lines):
            line = self.lines[self.index]

            if not line.strip():
                self.index += 1
                continue

            if line.startswith("```"):
                self.nodes.append(self.parse_code_block())
                continue

            if self.is_heading(line):
                self.nodes.append(self.parse_heading(line))
                self.index += 1
                continue

            if self.is_horizontal_rule(line):
                self.nodes.append(tag("hr"))
                self.index += 1
                continue

            if line.startswith(">"):
                self.nodes.append(self.parse_blockquote())
                continue

            if self.is_unordered_item(line):
                self.nodes.append(self.parse_list(ordered=False))
                continue

            if self.is_ordered_item(line):
                self.nodes.append(self.parse_list(ordered=True))
                continue

            self.nodes.append(self.parse_paragraph())

        return MarkdownDocument(self.nodes, self.headings)

    def parse_heading(self, line: str) -> Node:
        marker, text = line.split(" ", 1)
        level = min(len(marker), 3)
        slug = self.slugify(text)
        self.headings.append(Heading(level, text, slug))

        attrs = {"id": slug}
        children = self.inline(text)
        if level == 1:
            return h1(children, **attrs)
        if level == 2:
            return h2(children, **attrs)
        return h3(children, **attrs)

    def parse_code_block(self) -> Node:
        fence = self.lines[self.index]
        language = fence.strip().removeprefix("```").strip()
        self.index += 1
        code_lines: list[str] = []

        while self.index < len(self.lines) and not self.lines[self.index].startswith("```"):
            code_lines.append(self.lines[self.index])
            self.index += 1

        if self.index < len(self.lines):
            self.index += 1

        code = "\n".join(code_lines)
        attrs = {"class": code_class(language)} if language else {}
        return tag("pre", tag("code", highlight_code(code, language), **attrs))

    def parse_list(self, ordered: bool) -> Node:
        items: list[Node] = []

        while self.index < len(self.lines):
            line = self.lines[self.index]
            if ordered and not self.is_ordered_item(line):
                break
            if not ordered and not self.is_unordered_item(line):
                break

            text = re.sub(r"^\s*(?:[-*+]|\d+\.)\s+", "", line)
            items.append(li(self.inline(text)))
            self.index += 1

        return tag("ol" if ordered else "ul", items)

    def parse_blockquote(self) -> Node:
        lines: list[str] = []

        while self.index < len(self.lines) and self.lines[self.index].startswith(">"):
            lines.append(self.lines[self.index].removeprefix(">").strip())
            self.index += 1

        return tag("blockquote", p(self.inline(" ".join(lines))))

    def parse_paragraph(self) -> Node:
        lines: list[str] = []

        while self.index < len(self.lines):
            line = self.lines[self.index]
            if not line.strip():
                break
            if line.startswith("```") or self.is_heading(line) or self.is_horizontal_rule(line):
                break
            if line.startswith(">") or self.is_unordered_item(line) or self.is_ordered_item(line):
                break
            lines.append(line.strip())
            self.index += 1

        return p(self.inline(" ".join(lines)))

    def inline(self, text: str) -> list[Node | str]:
        pattern = re.compile(r"(`[^`]+`)|(\[[^\]]+\]\([^)]+\))")
        parts: list[Node | str] = []
        cursor = 0

        for match in pattern.finditer(text):
            if match.start() > cursor:
                parts.append(text[cursor : match.start()])

            token = match.group(0)
            if token.startswith("`"):
                parts.append(tag("code", token[1:-1]))
            else:
                link_match = re.match(r"\[([^\]]+)\]\(([^)]+)\)", token)
                if link_match is None:
                    parts.append(token)
                else:
                    label, href = link_match.groups()
                    parts.append(a(label, href=href))

            cursor = match.end()

        if cursor < len(text):
            parts.append(text[cursor:])

        return parts

    def is_heading(self, line: str) -> bool:
        return bool(re.match(r"^#{1,6}\s+\S", line))

    def is_horizontal_rule(self, line: str) -> bool:
        return bool(re.match(r"^\s*---+\s*$", line))

    def is_unordered_item(self, line: str) -> bool:
        return bool(re.match(r"^\s*[-*+]\s+\S", line))

    def is_ordered_item(self, line: str) -> bool:
        return bool(re.match(r"^\s*\d+\.\s+\S", line))

    def slugify(self, text: str) -> str:
        base = re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")
        if not base:
            base = "section"

        count = self.slug_counts.get(base, 0)
        self.slug_counts[base] = count + 1
        if count:
            return f"{base}-{count + 1}"
        return base


def code_class(language: str) -> str:
    normalized = normalize_language(language)
    classes = [f"language-{normalized or language}"]
    if normalized in {"bash", "html", "python"}:
        classes.append("has-highlight")
    return " ".join(classes)


def highlight_code(code: str, language: str) -> Any:
    normalized = normalize_language(language)
    if normalized == "python":
        return raw_html(highlight_lines(code, highlight_python_line))
    if normalized == "bash":
        return raw_html(highlight_lines(code, highlight_bash_line))
    if normalized == "html":
        return raw_html(highlight_html(code))
    return raw_html(escape(code, quote=False))


def raw_html(html: str) -> Any:
    return cast(Any, getattr(_components, "RawHtml"))(html)


def normalize_language(language: str) -> str:
    value = language.lower().strip()
    aliases = {
        "console": "bash",
        "html": "html",
        "py": "python",
        "python": "python",
        "sh": "bash",
        "shell": "bash",
        "zsh": "bash",
    }
    return aliases.get(value, value)


def highlight_lines(code: str, highlighter) -> str:
    return "\n".join(highlighter(line) for line in code.split("\n"))


def highlight_python_line(line: str) -> str:
    return highlight_regex_line(line, PYTHON_TOKEN_RE, python_token_class)


def python_token_class(kind: str, value: str, line: str, end: int) -> str | None:
    if kind == "comment":
        return "tok-comment"
    if kind == "string":
        return "tok-string"
    if kind == "number":
        return "tok-number"
    if kind == "decorator":
        return "tok-decorator"
    if kind == "operator":
        return "tok-operator"
    if kind == "name":
        if value in PYTHON_KEYWORDS:
            return "tok-keyword"
        if value in PYTHON_BUILTINS:
            return "tok-builtin"
        if next_nonspace(line, end) == "(":
            return "tok-call"
    return None


def highlight_bash_line(line: str) -> str:
    first_word = True

    def token_class(kind: str, value: str, current_line: str, end: int) -> str | None:
        nonlocal first_word
        if kind == "comment":
            return "tok-comment"
        if kind == "string":
            return "tok-string"
        if kind == "option":
            return "tok-option"
        if kind == "variable":
            return "tok-variable"
        if kind == "operator":
            return "tok-operator"
        if kind == "word":
            if first_word or value in BASH_COMMANDS:
                first_word = False
                return "tok-command"
            first_word = False
        return None

    return highlight_regex_line(line, BASH_TOKEN_RE, token_class)


def highlight_html(code: str) -> str:
    pattern = re.compile(
        r"(?P<comment><!--.*?-->)"
        r"|(?P<tag></?[\w:-]+)"
        r"|(?P<attr>\b[\w:-]+)(?=\=)"
        r"|(?P<string>\"[^\"]*\"|'[^']*')"
        r"|(?P<bracket>/?>)",
        re.DOTALL,
    )
    class_map = {
        "comment": "tok-comment",
        "tag": "tok-keyword",
        "attr": "tok-attribute",
        "string": "tok-string",
        "bracket": "tok-operator",
    }
    return highlight_regex_line(
        code,
        pattern,
        lambda kind, value, line, end: class_map.get(kind),
    )


def highlight_regex_line(line: str, pattern: re.Pattern[str], classifier) -> str:
    parts: list[str] = []
    cursor = 0

    for match in pattern.finditer(line):
        if match.start() > cursor:
            parts.append(escape(line[cursor : match.start()], quote=False))

        value = match.group(0)
        kind = match.lastgroup or ""
        class_name = classifier(kind, value, line, match.end())
        escaped = escape(value, quote=False)
        if class_name:
            parts.append(f'<span class="{class_name}">{escaped}</span>')
        else:
            parts.append(escaped)

        cursor = match.end()

    if cursor < len(line):
        parts.append(escape(line[cursor:], quote=False))

    return "".join(parts)


def next_nonspace(line: str, start: int) -> str:
    for char in line[start:]:
        if not char.isspace():
            return char
    return ""
