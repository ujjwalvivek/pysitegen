# pysitegen

pysitegen is a tiny Python-authored static site generator. You write pages with Python primitives, choose a default terminal-dark theme, add optional behaviors, and build plain HTML, CSS, and JavaScript. The goal is to make the web comfortable to author from Python while keeping the output boring, inspectable, and easy to host anywhere.

## What You Can Build

- Static landing pages
- Personal portfolio and resume sites
- Documentation sites
- Collection or showcase pages
- SPA-style sites with hash routes

The framework gives you primitives. Your project owns the structure.

## Project Layout

A new site starts with a small, explicit structure:

```text

my-site/
  index.py
  assets/
    index.css
  content/
    docs/
      .gitkeep
  static/
    favicon.png
    robots.txt
  .gitignore
  README.md
```

`index.py` is the default page and build entry. `assets/` holds authored CSS and other page assets. `static/` holds files that should be copied directly to the public output. `content/docs/` is ready for Markdown content. Build output is written to `public/`. Treat `public/` as generated output, not source.

## Build And Preview

Install PySiteGen from PyPI:

```bash

python -m pip install pysitegen
```

Create a new site:

```bash

pysitegen init my-site
cd my-site
pysitegen serve
```

That creates the starter project, builds it, watches for file changes, and reloads the browser tab automatically. Open:

```text

http://127.0.0.1:8000/
```

Run a clean build from a site folder:

```bash

pysitegen build
```

That deletes `public/` and rebuilds the configured pages. You can add a `site.py` later when the project needs multiple pages or custom output paths.

Run a compile+build:

```bash

pysitegen compile
pysitegen build
```

These commands check Python files and clears the generated `__pycache__` directories afterward. From a site folder it checks the site entry files and `pages/` when they exist. You can also pass explicit files or directories.

Preview the generated site over HTTP:

```bash

pysitegen serve --host 127.0.0.1 --port 8000
```

Open:

```text

http://127.0.0.1:8000/
```

HTTP preview avoids browser restrictions around scripts, modules, assets, and future fetch-based features. If you want to access the preview through a machine name or from another device on your network, bind to all interfaces, then open the host name or LAN address for that machine:

```bash

pysitegen serve --host 0.0.0.0 --port 8000
```

Use `pysitegen serve --no-reload` when you want the plain static server without watching or browser reload.

## Your First Page

A page is a Python module with a `build()` function that returns a `Document`.

```python

from pysitegen import a, default_dark, h1, p, page, section


def build():
    return page(
        section(
            p("Hello from Python", class_="eyebrow"),
            h1("My Site"),
            p("This page was generated from Python primitives.", class_="muted"),
            a("Read docs", href="#docs", class_="button primary"),
            class_="container stack",
        ),
        title="My Site",
        description="A tiny generated page.",
        theme=default_dark(),
    )
```

Save the page as `index.py` and run:

```bash

pysitegen build
```

## HTML Primitives

The public package exports common HTML helpers:

```python

from pysitegen import a, article, button, div, h1, h2, h3, img, li, p, section, tag, ul
```

Most helpers accept children first and attributes as keyword arguments:

```python

section(
    h2("Selected Work"),
    p("A compact project list.", class_="muted"),
    class_="container stack",
    id="work",
)
```

Use `tag()` when a primitive does not exist yet:

```python

tag("input", name="email", type="email", placeholder="you@example.com")
```

## Project Files

For a one-page site, `index.py` is enough.

For multiple pages or custom output paths, add `site.py`:

```python

SITE = {
    "output": "public",
    "static": "static",
    "pages": [
        ("index.py", ""),
        ("pages/about.py", "about"),
    ],
}
```

Each page module must define:

```python

def build():
    ...
```

and return a `Document` created by `page(...)`.

## Assets

There are two asset paths.

Site-owned public files go in `static/`:

```bash

static/
  favicon.png
  robots.txt
```

They are copied directly:

```bash

public/favicon.png
public/robots.txt
```

Page assets go through `asset(...)`:

```python

from pathlib import Path
from pysitegen import asset, default_dark, h1, page, section

ROOT = Path(__file__).resolve().parent
ASSETS = ROOT / "assets"

def build():
    return page(
        section(h1("Styled")),
        title="Styled",
        theme=default_dark(),
        assets=[asset(ASSETS / "index.css", "assets/index.css")],
        stylesheets=["assets/index.css"],
    )
```

Use `asset(source, target)` to copy files into the generated output.

```python

from pysitegen import asset, page

page(
    ...,
    assets=[
        asset("assets/site.css", "assets/site.css"),
        asset("assets/index.js", "assets/index.js"),
    ],
    stylesheets=["assets/site.css"],
    scripts=["assets/index.js"],
)
```

The renderer copies each source file to the requested target under the output directory.

## Themes

The default theme is intentionally opinionated about taste but not page architecture.

```python

from pysitegen import default_dark

page(..., theme=default_dark())
```

The default theme provides:

- Dark terminal-inspired colors
- Mono-flavored headings and controls
- Layout utilities like `container`, `stack`, `cluster`, and `grid`
- Reusable surfaces like `panel`, `card`, and `terminal-frame`
- Controls like `button`, `tag`, `muted`, `eyebrow`, and `accent-text`
- Documentation styles for Markdown-rendered pages

You can override the look with page-specific CSS.

## SPA Behavior

The `spa()` behavior adds hash-route navigation.

```python

from pysitegen import page, section, spa

page(
    nav(...),
    main(
        section(..., id="home", data_route_panel="home", class_="route-panel active"),
        section(..., id="docs", data_route_panel="docs", class_="route-panel"),
    ),
    behaviors=[spa()],
)
```

Links opt in with `data_route`:

```python

a("Docs", href="#docs", data_route="docs")
```

The behavior:

- Shows the active route panel
- Hides inactive panels
- Updates active link styling
- Sets `aria-current="page"`
- Scrolls the active panel into view
- Accounts for sticky nav height using `data_sticky_nav`

## Visual Canvas

pysitegen can render procedural canvas scenes from Python-authored scene data. The Python side describes the scene. The Substrate runtime is loaded from the CDN only when `canvas_background()` is used. This keeps generated projects small, but pages using this behavior need network access when they load.

```python

from pysitegen import canvas_background, page, visual_canvas, visual_scene

scene = visual_scene(
    "background",
    ("grid", {"spacing": 96, "opacity": 0.35}),
    ("nodes", {"count": 24, "opacity": 0.8}),
    ("vignette", {"opacity": 0.7}),
)

page(
    visual_canvas(scene, id="hero-canvas", fps=0, class_="hero-visual"),
    title="Visual",
    behaviors=[canvas_background()],
)
```

The canvas is explicit so your CSS controls size and placement:

```css

.hero-visual {
  display: block;
  width: 100%;
  height: 420px;
}
```

Built-in primitives:

- `background`
- `grid`
- `scanlines`
- `particles`
- `nodes`
- `wireframes`
- `branches`
- `mandala`
- `streams`
- `glitch`
- `vignette`
- `foam`
- `hyperstring`
- `topography`

Animation is opt-in. `fps=0` renders a static frame. Positive values animate at that target frame rate, and the runtime falls back to static rendering when the visitor prefers reduced motion.

## Markdown Documents

pysitegen can render Markdown into `Node` trees. Markdown content still goes through the same renderer, escaping, theme, and asset pipeline.

```python

from pysitegen import markdown_file, markdown_toc

doc = markdown_file(ROOT / "content" / "docs" / "getting-started.md")

section(
    markdown_toc(doc),
    article(doc.nodes, class_="docs-content"),
    class_="docs-layout",
)
```

The first parser supports:

- Headings
- Paragraphs
- Unordered lists
- Ordered lists
- Fenced code blocks
- Inline code
- Links
- Blockquotes
- Horizontal rules

It is intentionally small. For now, the value is that the output remains native to pysitegen.

## Build Configuration

`site.py` owns the pages that become part of the generated site.

For a one-page site, you can skip `site.py` and use `index.py` directly:

```python

from pysitegen import default_dark, h1, p, page, section


def build():
    return page(
        section(h1("Hello"), p("Generated from index.py.")),
        title="Hello",
        theme=default_dark(),
    )
```

When `site.py` is absent, `pysitegen build` and `pysitegen serve` use
`index.py`.

For a larger site, add `site.py`:

```python

SITE = {
    "output": "public",
    "static": "static",
    "pages": [
        ("index.py", ""),
        ("pages/about.py", "about"),
    ],
}
```

Add a new page by appending a new `(source, output)` pair. The configured static folder is copied directly into `public/` before pages are rendered. This is the Zola-like path for files that should exist at stable public URLs.

## CLI

```bash

pysitegen init [path]
pysitegen build [--config site.py]
pysitegen serve [--config site.py] [--host 127.0.0.1] [--port 8000] [--no-reload]
pysitegen compile [paths...]
pysitegen --version
```

`build` and `serve` look for `site.py`, then `index.py`.

`serve` rebuilds when source files change and injects a temporary reload script into served HTML responses. Generated files on disk stay normal static output.

`compile` runs Python bytecode checks and removes generated `__pycache__` directories afterward.

Useful checks from the PySiteGen source repository:

```bash

pysitegen compile src website
```

## API Reference

Import from the public package facade:

```python

from pysitegen import (
    page,
    section,
    h1,
    p,
    a,
    asset,
    default_dark,
    spa,
    visual_scene,
    visual_canvas,
    canvas_background,
)
```

Avoid importing from internal modules such as `pysitegen.theme`, `pysitegen.md`, `pysitegen.renderer`, or `pysitegen.builder` in normal site code. Those modules exist, but the package root is the stable authoring surface. Use the `pysitegen` CLI for build, serve, init, and compile workflows.

### Page And Document

`page(*body, title: str, description: str | None = None, lang: str = "en", assets=(), stylesheets=(), scripts=(), module_scripts=(), behaviors=(), head=(), theme: Theme | None = None) -> Document`

Creates a `Document`. A page module should return this from `build()`.

```python

from pysitegen import h1, page, section

def build():
    return page(
        section(h1("Hello")),
        title="Hello",
        description="A static page.",
    )
```

`Document`

The object returned by `page(...)`. The builder expects every page module's `build()` function to return a `Document`.

### HTML Primitives

`div(*children, **attrs) -> Node`, `section(*children, **attrs) -> Node`, `article(*children, **attrs) -> Node`, `main(*children, **attrs) -> Node`, `nav(*children, **attrs) -> Node`, `h1(*children, **attrs) -> Node`, `h2(*children, **attrs) -> Node`, `h3(*children, **attrs) -> Node`, `p(*children, **attrs) -> Node`, `a(*children, **attrs) -> Node`, `button(*children, **attrs) -> Node`, `canvas(**attrs) -> Node`, `footer(*children, **attrs) -> Node`, `header(*children, **attrs) -> Node`, `hr(**attrs) -> Node`, `img(**attrs) -> Node`, `li(*children, **attrs) -> Node`, `script(*children, **attrs) -> Node`, `span(*children, **attrs) -> Node`, `ul(*children, **attrs) -> Node`

Convenience helpers for common HTML tags. Children come first. Attributes are keyword arguments.

```python

from pysitegen import a, h2, p, section

section(
    h2("Docs"),
    p("Generated from Python."),
    a("Read more", href="#more", class_="button"),
    class_="container stack",
)
```

`tag(tag_name: str, *children, **attrs) -> Node`

Creates any HTML element when there is no dedicated helper.

```python

from pysitegen import tag

tag("input", type="email", name="email", aria_label="Email")
```

Attribute names are normalized:

- `class_` becomes `class`
- `aria_label` becomes `aria-label`
- `data_route_panel` becomes `data-route-panel`
- `True` renders a boolean attribute
- `False` and `None` omit the attribute

### Assets

`asset(source: str | Path, target: str) -> Asset`

Registers a file to copy during rendering. `source` is the file on disk. `target` is the path inside the generated output directory.

```python

from pathlib import Path
from pysitegen import asset, page

ROOT = Path(__file__).resolve().parent

page(
    ...,
    assets=[asset(ROOT / "assets" / "index.css", "assets/index.css")],
    stylesheets=["assets/index.css"],
)
```

Use `static/` for files that should copy directly to the root of `public/`, such as `favicon.png` or `robots.txt`. Use `asset(...)` for files explicitly required by a page.

### Theme And Behavior

`default_dark() -> Theme`

Returns the bundled terminal-dark theme. It adds `pysitegen.css` to the page asset list and stylesheet list.

```python

from pysitegen import default_dark, page

page(..., title="Themed", theme=default_dark())
```

`spa() -> Behavior`

Adds hash-route behavior and copies the bundled `pysitegen-spa.js` script.

```python

from pysitegen import main, page, section, spa

page(
    main(
        section(..., data_route_panel="home", class_="route-panel active"),
        section(..., data_route_panel="docs", class_="route-panel"),
    ),
    title="Routes",
    behaviors=[spa()],
)
```

`visual_scene(*layers) -> Scene`

Creates serializable scene data for the Substrate canvas runtime. A layer can be a primitive name or a `(primitive, options)` tuple.

```python

from pysitegen import visual_scene

scene = visual_scene(
    "background",
    ("grid", {"spacing": 120}),
)
```

`visual_canvas(scene, *, id: str, fps: int = 0, palette=None, **attrs) -> Node`

Creates a `<canvas>` with the scene stored as HTML data attributes. Pass normal HTML attributes such as `class_`, `aria_label`, or `data_*` as keyword arguments.

```python

from pysitegen import visual_canvas

visual_canvas(scene, id="hero-canvas", fps=30, class_="hero-visual")
```

`canvas_background(runtime: str = "https://cdn.ujjwalvivek.com/scripts/substrate/latest/main.js") -> Behavior`

Adds a tiny module adapter that imports the Substrate runtime from the CDN and binds every `visual_canvas(...)` on the page. Use it in `behaviors=[...]` on any page that contains a `visual_canvas(...)`.

### Markdown

`markdown_file(path: str | Path) -> MarkdownDocument`

Reads a Markdown file and returns a `MarkdownDocument` with `nodes` and `headings`.

`markdown_text(text: str) -> MarkdownDocument`

Parses a Markdown string and returns a `MarkdownDocument`.

`markdown_toc(document: MarkdownDocument, title: str = "On this page", collapsible: bool = False, open: bool = False) -> Node`

Builds a table of contents from level-2 and level-3 headings.

Use `collapsible=True` for a TOC that stays visible on desktop and collapses on smaller screens. Set `open=True` when the mobile TOC should start expanded.

```python

from pysitegen import article, markdown_file, markdown_toc, section

doc = markdown_file("content/docs/getting-started.md")

section(
    markdown_toc(doc, collapsible=True),
    article(doc.nodes, class_="docs-content"),
    class_="docs-layout",
)
```

## Developing PySiteGen Itself

Most users should install from PyPI:

```bash

python -m pip install pysitegen
```

If you are working on the PySiteGen package source, clone the repository and use an editable install from the repo root:

```bash

python -m pip install -e .[dev]
python -m pytest
```

This repository contains the package and the website source:

```text

pysitegen/
  pyproject.toml
  src/
    pysitegen/
  website/
    index.py
    content/docs/getting-started.md
    assets/
    static/
```

## What now?

The website is intentionally just another PySiteGen consumer. It imports from `pysitegen` like any other site. The current version is small on purpose. It is a foundation for testing how far Python-authored websites can go while still producing normal static files.
