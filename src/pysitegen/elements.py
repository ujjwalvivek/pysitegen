from __future__ import annotations

from typing import Iterable

from .behaviors import Behavior
from .components import Asset, Document, Node, RawHtml, flatten
from .theme import Theme


Child = Node | RawHtml | str | Iterable[Node | RawHtml | str]
AttrValue = str | int | float | bool | None


def page(
    *body: Child,
    title: str,
    description: str | None = None,
    lang: str = "en",
    assets: Iterable[Asset] = (),
    stylesheets: Iterable[str] = (),
    scripts: Iterable[str] = (),
    module_scripts: Iterable[str] = (),
    behaviors: Iterable[Behavior] = (),
    head: Iterable[Node] = (),
    theme: Theme | None = None,
) -> Document:
    page_assets = list(assets)
    page_stylesheets = list(stylesheets)
    page_scripts = list(scripts)
    page_module_scripts = list(module_scripts)
    page_head = list(head)

    if theme:
        page_assets = [*theme.assets, *page_assets]
        page_stylesheets = [*theme.stylesheets, *page_stylesheets]

    for behavior in behaviors:
        page_assets = [*behavior.assets, *page_assets]
        page_scripts = [*behavior.scripts, *page_scripts]
        page_module_scripts = [*behavior.module_scripts, *page_module_scripts]
        page_head = [*behavior.head, *page_head]

    return Document(
        title=title,
        description=description,
        lang=lang,
        body=flatten(body),
        assets=page_assets,
        stylesheets=page_stylesheets,
        scripts=page_scripts,
        module_scripts=page_module_scripts,
        head=page_head,
    )


def tag(tag_name: str, *children: Child, **attrs: AttrValue) -> Node:
    return Node(tag_name, flatten(children), attrs)


def a(*children: Child, **attrs: AttrValue) -> Node:
    return tag("a", *children, **attrs)


def article(*children: Child, **attrs: AttrValue) -> Node:
    return tag("article", *children, **attrs)


def body(*children: Child, **attrs: AttrValue) -> Node:
    return tag("body", *children, **attrs)


def button(*children: Child, **attrs: AttrValue) -> Node:
    return tag("button", *children, **attrs)


def canvas(**attrs: AttrValue) -> Node:
    return tag("canvas", **attrs)


def div(*children: Child, **attrs: AttrValue) -> Node:
    return tag("div", *children, **attrs)


def footer(*children: Child, **attrs: AttrValue) -> Node:
    return tag("footer", *children, **attrs)


def h1(*children: Child, **attrs: AttrValue) -> Node:
    return tag("h1", *children, **attrs)


def h2(*children: Child, **attrs: AttrValue) -> Node:
    return tag("h2", *children, **attrs)


def h3(*children: Child, **attrs: AttrValue) -> Node:
    return tag("h3", *children, **attrs)


def header(*children: Child, **attrs: AttrValue) -> Node:
    return tag("header", *children, **attrs)


def hr(**attrs: AttrValue) -> Node:
    return tag("hr", **attrs)


def img(**attrs: AttrValue) -> Node:
    return tag("img", **attrs)


def li(*children: Child, **attrs: AttrValue) -> Node:
    return tag("li", *children, **attrs)


def main(*children: Child, **attrs: AttrValue) -> Node:
    return tag("main", *children, **attrs)


def nav(*children: Child, **attrs: AttrValue) -> Node:
    return tag("nav", *children, **attrs)


def p(*children: Child, **attrs: AttrValue) -> Node:
    return tag("p", *children, **attrs)


def script(*children: Child, **attrs: AttrValue) -> Node:
    return tag("script", *children, **attrs)


def section(*children: Child, **attrs: AttrValue) -> Node:
    return tag("section", *children, **attrs)


def span(*children: Child, **attrs: AttrValue) -> Node:
    return tag("span", *children, **attrs)


def ul(*children: Child, **attrs: AttrValue) -> Node:
    return tag("ul", *children, **attrs)
