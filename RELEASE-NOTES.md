## PySiteGen v1.0.0

### Highlights

- pysitegen serve` now builds once, watches the site folder, rebuilds on changes, and reloads the browser automatically.
- It ignores generated output like `public/`, plus `.venv`, `.git`, `__pycache__`, cache dirs, etc.
- Served HTML gets a temporary EventSource reload script injected at request time, so generated files on disk stay clean.
- Added `pysitegen serve --no-reload` for the old plain static server behavior.
- Clears cached project modules before builds so changed helper imports are picked up.

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
