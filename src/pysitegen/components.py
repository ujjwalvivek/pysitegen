from __future__ import annotations

from dataclasses import dataclass, field
from html import escape
from pathlib import Path
from typing import Iterable


Attrs = dict[str, str | int | float | bool | None]


VOID_TAGS = {
    "area",
    "base",
    "br",
    "col",
    "embed",
    "hr",
    "img",
    "input",
    "link",
    "meta",
    "source",
    "track",
    "wbr",
}


@dataclass(frozen=True)
class Asset:
    source: Path
    target: str


@dataclass(frozen=True)
class RawHtml:
    html: str


@dataclass
class Node:
    tag: str
    children: list[Node | RawHtml | str] = field(default_factory=list)
    attrs: Attrs = field(default_factory=dict)

    def render(self, indent: int = 0) -> str:
        pad = " " * indent
        attrs = _render_attrs(self.attrs)

        if self.tag in VOID_TAGS:
            return f"{pad}<{self.tag}{attrs}>"

        if not self.children:
            return f"{pad}<{self.tag}{attrs}></{self.tag}>"

        if len(self.children) == 1 and isinstance(self.children[0], str):
            text = escape(self.children[0], quote=False)
            return f"{pad}<{self.tag}{attrs}>{text}</{self.tag}>"

        if len(self.children) == 1 and isinstance(self.children[0], RawHtml):
            return f"{pad}<{self.tag}{attrs}>{self.children[0].html}</{self.tag}>"

        rendered_children = "\n".join(_render_child(child, indent + 2) for child in self.children)
        return f"{pad}<{self.tag}{attrs}>\n{rendered_children}\n{pad}</{self.tag}>"


@dataclass
class Document:
    title: str
    body: list[Node | RawHtml | str]
    assets: list[Asset] = field(default_factory=list)
    lang: str = "en"
    description: str | None = None
    stylesheets: list[str] = field(default_factory=list)
    scripts: list[str] = field(default_factory=list)
    module_scripts: list[str] = field(default_factory=list)
    head: list[Node] = field(default_factory=list)

    def render(self) -> str:
        head_nodes: list[Node | RawHtml | str] = [
            Node("meta", attrs={"charset": "UTF-8"}),
            Node("meta", attrs={"name": "viewport", "content": "width=device-width, initial-scale=1.0"}),
            Node("title", [self.title]),
        ]

        if self.description:
            head_nodes.append(Node("meta", attrs={"name": "description", "content": self.description}))

        head_nodes.extend(Node("link", attrs={"rel": "stylesheet", "href": href}) for href in self.stylesheets)
        head_nodes.extend(self.head)

        body_nodes: list[Node | RawHtml | str] = list(self.body)
        body_nodes.extend(Node("script", attrs={"src": src, "defer": True}) for src in self.scripts)
        body_nodes.extend(Node("script", attrs={"type": "module", "src": src}) for src in self.module_scripts)

        html = Node(
            "html",
            [
                Node("head", head_nodes),
                Node("body", body_nodes),
            ],
            attrs={"lang": self.lang},
        )

        return "<!DOCTYPE html>\n" + html.render() + "\n"


def tag(tag_name: str, *children: Node | RawHtml | str, **attrs: str | int | float | bool | None) -> Node:
    return Node(tag_name, list(children), attrs)


def div(*children: Node | RawHtml | str, **attrs: str | int | float | bool | None) -> Node:
    return tag("div", *children, **attrs)


def text_node(tag_name: str, text: str, class_name: str | None = None) -> Node:
    attrs: Attrs = {}
    if class_name:
        attrs["class"] = class_name
    return Node(tag_name, [text], attrs)


def flatten(nodes: Iterable[Node | RawHtml | str | Iterable[Node | RawHtml | str]]) -> list[Node | RawHtml | str]:
    result: list[Node | RawHtml | str] = []
    for node in nodes:
        if isinstance(node, Node) or isinstance(node, RawHtml) or isinstance(node, str):
            result.append(node)
        else:
            result.extend(flatten(node))
    return result


def _render_child(child: Node | RawHtml | str, indent: int) -> str:
    if isinstance(child, Node):
        return child.render(indent)

    if isinstance(child, RawHtml):
        return " " * indent + child.html

    return " " * indent + escape(child, quote=False)


def _render_attrs(attrs: Attrs) -> str:
    rendered: list[str] = []
    for key, value in attrs.items():
        if value is None or value is False:
            continue
        html_key = key.rstrip("_").replace("_", "-")
        if value is True:
            rendered.append(html_key)
            continue
        rendered.append(f'{html_key}="{escape(str(value), quote=True)}"')

    if not rendered:
        return ""

    return " " + " ".join(rendered)
