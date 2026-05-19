## PySiteGen v1.1.0

### Highlights

- Tightened the root `pysitegen` public API.
  - The root package now focuses on the authoring facade: page primitives, assets, themes, behaviors, and Markdown helpers.
  - Builder/render helpers are no longer exported from the root package.
  - CLI commands remain the supported build/serve/init/compile workflow.
- Updated API documentation with clearer, typed signatures for stable authoring helpers.
- Updated starter/docs guidance around `pysitegen serve`.
- Added tests for root public API boundaries

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
