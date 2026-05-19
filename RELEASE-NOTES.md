## PySiteGen v1.2.0

### Highlights

- Fixed local source-tree `--version` behavior so it reads the project version from `pyproject.toml`.
- Added visual scene helpers:
  - `visual_scene(...)`
  - `visual_canvas(...)`
  - `canvas_background(...)`
- `canvas_background()` now loads the Substrate runtime from CDN only when a page opts in. No large canvas runtime is bundled.
- Added docs and tests for the visual canvas API.
- Canvas scenes support Substrate primitives such as `background`, `grid`, `particles`, `nodes`, `streams`, `scanlines`, `topography`, `vignette`, and [!more](https://cdn.ujjwalvivek.com/scripts/substrate/latest/readme.md).

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
