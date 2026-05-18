from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

from .components import Node
from .elements import a, h1, h2, h3, li, p, tag, ul


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


def markdown_toc(document: MarkdownDocument, title: str = "On this page") -> Node:
    items = [
        li(a(heading.text, href=f"#{heading.slug}", class_=f"toc-link level-{heading.level}"))
        for heading in document.headings
        if heading.level in {2, 3}
    ]

    return tag(
        "aside",
        p(title, class_="eyebrow"),
        ul(items, class_="docs-toc-list"),
        class_="docs-toc",
    )


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

        attrs = {"class": f"language-{language}"} if language else {}
        return tag("pre", tag("code", "\n".join(code_lines), **attrs))

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
