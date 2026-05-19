# PySiteGen

## Python-authored static sites.

PySiteGen is a small static site generator for people who would rather compose HTML with Python without any runtime server, client framework, or hidden build graph. PySiteGen gives you primitives. The default visual taste is just a theme layer with terminal-dark aesthetics. It is practical. You write Python functions that return HTML nodes. PySiteGen renders them to static HTML and copies the assets you explicitly ask for. It produces plain files:

```bash
public/
  index.html
  assets/
  favicon.png
  robots.txt
```

Works for docs sites, small product or project pages, personal sites, link hubs, simple SPA-style hash routes, and static pages that benefit from Python data and composition.


## Install

```bash
python -m pip install pysitegen
pysitegen --version
```

## Start A Site

```bash
pysitegen init my-site
cd my-site
pysitegen serve
```

`serve` builds once, watches your site files, rebuilds when they change, and reloads the browser tab automatically.

## A Page

```python
from pysitegen import a, default_dark, h1, p, page, section

def build():
    return page(
        section(
            p("PySiteGen", class_="eyebrow"),
            h1("Hello from Python."),
            p("This is a static page generated from Python primitives.", class_="muted"),
            a("Read more", href="#more", class_="button primary"),
            class_="container stack",
        ),
        title="Hello",
        description="A PySiteGen page.",
        theme=default_dark(),
    )
```

Build it and serve it:

```bash
pysitegen build
pysitegen serve --host 127.0.0.1 --port 8000
```

Use `pysitegen serve --no-reload` when you want the plain static server.

## This Repo

This repository contains the package source, tests, and the real PySiteGen website:

```text
src/pysitegen/  package source and bundled framework assets
tests/          fixture-based behavior tests
website/        PySiteGen website source
```

Develop locally:

```bash
python -m pip install -e .[dev]
python -m pytest
```

Build and serve the website:

```bash
cd website
pysitegen build
pysitegen serve --host 127.0.0.1 --port 8000
```

Do not edit `website/public/` as source.

## Current Limits

PySiteGen is small on purpose.

- The Markdown parser is intentionally limited.
- There is no template/layout system yet.
- There is no plugin system.
- The default theme is useful, not universal.
- The API is still young.
