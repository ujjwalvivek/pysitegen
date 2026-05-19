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

That creates the starter project, builds it, and serves it locally. Open:

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
        asset("assets/site.js", "assets/site.js"),
    ],
    stylesheets=["assets/site.css"],
    scripts=["assets/site.js"],
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
pysitegen serve [--config site.py] [--host 127.0.0.1] [--port 8000]
pysitegen compile [paths...]
pysitegen --version
```

`build` and `serve` look for `site.py`, then `index.py`.

`compile` runs Python bytecode checks and removes generated `__pycache__` directories afterward.

Useful checks from the PySiteGen source repository:

```bash
pysitegen compile src website
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

The website is intentionally just another PySiteGen consumer. It imports from `pysitegen` like any other site.

## Where To Go Next

Useful next improvements:

- A richer Markdown parser
- Automatic code highlighting
- Browser screenshot verification
- Better build configuration
- More behaviors for tabs, accordions, and copy buttons

The current version is small on purpose. It is a foundation for testing how far Python-authored websites can go while still producing normal static files.
