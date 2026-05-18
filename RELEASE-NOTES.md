## PySiteGen v0.1.0

Initial public release of PySiteGen, a small Python-authored static site generator for building plain static websites with composable Python primitives.

### Highlights

- Added the core `pysitegen` package with a proper `src/` layout.
- Added the `pysitegen` CLI entry point.
- Added starter project generation with `pysitegen init`.
- Added static site build support with `pysitegen build`.
- Added local serving support with `pysitegen serve`.
- Added compile checking and cache cleanup with `pysitegen compile`.
- Added bundled framework assets:
  - `pysitegen.css`
  - `pysitegen-spa.js`
  - default favicon
- Added public Python APIs for building pages:
  - HTML primitives like `h1`, `p`, `section`, `a`, `div`
  - `page()`
  - `asset()`
  - `default_dark()`
  - `spa()`
  - Markdown helpers
- Added support for single-page `index.py` projects.
- Added support for multi-page `site.py` configurations.
- Added direct copying of user-owned `static/` files into `public/`.
- Added authored asset copying into `public/assets/`.

### Testing

This release includes a pytest suite covering the main user workflows:

- starter project creation
- default `index.py` builds
- multi-page `site.py` builds
- static file copying
- authored asset copying
- bundled theme and SPA asset copying
- output directory cleanup
- CLI version output
- compile cache cleanup
- common error cases

### Packaging

- Added MIT license.
- Added PyPI-ready project metadata.
- Added package manifest for source distributions.
- Added GitHub Actions publishing workflow for PyPI releases.

### Install

```bash
python -m pip install pysitegen
```

### Start a Site

```bash
pysitegen init my-site
cd my-site
pysitegen build
pysitegen serve
```
