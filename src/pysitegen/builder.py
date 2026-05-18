from __future__ import annotations

import argparse
import compileall
import http.server
import importlib.util
import importlib.metadata
import shutil
import sys
from dataclasses import dataclass
from functools import partial
from pathlib import Path
from types import ModuleType
from typing import Iterable

from .components import Document
from .renderer import render_site


PACKAGE_ROOT = Path(__file__).resolve().parent
STARTER_INDEX = '''from pathlib import Path

from pysitegen import a, asset, default_dark, h1, h2, p, page, section, tag


ROOT = Path(__file__).resolve().parent
ASSETS = ROOT / "assets"


def build():
    return page(
        section(
            p("PySiteGen", class_="eyebrow"),
            h1("Your Python-authored static site is running."),
            p(
                "Edit index.py and assets/index.css, then run pysitegen build.",
                class_="muted",
            ),
            a("Next steps", href="#next", class_="button primary"),
            class_="container stack starter-hero",
        ),
        section(
            p("Next steps", class_="eyebrow"),
            h2("Make it yours."),
            p("Change the structure in index.py and the page-specific styling in assets/index.css."),
            p("Generated files land in public/, which is ignored by git."),
            id="next",
            class_="container stack",
        ),
        title="My PySiteGen Site",
        description="A static site generated with PySiteGen.",
        head=[tag("link", rel="icon", type="image/png", href="/favicon.png")],
        theme=default_dark(),
        assets=[asset(ASSETS / "index.css", "assets/index.css")],
        stylesheets=["assets/index.css"],
    )
'''
STARTER_CSS = """.starter-hero {
  min-height: 70vh;
  justify-content: center;
}
"""
STARTER_README = """# My PySiteGen Site

Build the site:

```powershell
pysitegen build
```

Preview locally:

```powershell
pysitegen serve --host 127.0.0.1 --port 8000
```

Check Python files and clean generated cache files:

```powershell
pysitegen compile
```

Edit `index.py` for page structure and `assets/index.css` for page-specific styles.
Generated output is written to `public/`.
"""
STARTER_GITIGNORE = """public/
__pycache__/
*.egg-info/
.venv/
"""


@dataclass(frozen=True)
class PageSpec:
    source: Path
    output: Path


@dataclass(frozen=True)
class SiteConfig:
    root: Path
    package_root: Path
    output: Path
    static: Path | None
    pages: list[PageSpec]


def main() -> None:
    parser = argparse.ArgumentParser(description="Build, serve, verify, and start pysitegen sites.")
    parser.add_argument("--version", action="version", version=f"%(prog)s {package_version()}")
    subparsers = parser.add_subparsers(dest="command", required=True)

    init_parser = subparsers.add_parser("init", help="Create a starter pysitegen site")
    init_parser.add_argument("path", nargs="?", default=".", help="Project directory to create")

    build_parser = subparsers.add_parser("build", help="Build the current site")
    build_parser.add_argument("--config", help="Config or page file. Defaults to site.py, then index.py")

    serve_parser = subparsers.add_parser("serve", help="Build and serve the current site")
    serve_parser.add_argument("--config", help="Config or page file. Defaults to site.py, then index.py")
    serve_parser.add_argument("--host", default="127.0.0.1", help="Host for serve")
    serve_parser.add_argument("--port", type=int, default=8000, help="Port for serve")

    compile_parser = subparsers.add_parser("compile", help="Compile-check Python files and clean caches")
    compile_parser.add_argument("paths", nargs="*", help="Files or directories to check")

    args = parser.parse_args()

    try:
        run_command(args, parser)
    except RuntimeError as error:
        parser.exit(1, f"pysitegen: error: {error}\n")


def run_command(args: argparse.Namespace, parser: argparse.ArgumentParser) -> None:
    if args.command == "init":
        init_project(Path(args.path))
        return

    if args.command == "compile":
        compile_project(args.paths)
        return

    config = load_config(args.config)

    if args.command == "build":
        build(config)
    else:
        build(config)
        serve(config.output, args.host, args.port)


def package_version() -> str:
    try:
        return importlib.metadata.version("pysitegen")
    except importlib.metadata.PackageNotFoundError:
        return "0.1.0"


def load_config(path: str | Path | None = None) -> SiteConfig:
    config_path = resolve_config_path(path)
    root = config_path.parent

    if str(root) not in sys.path:
        sys.path.insert(0, str(root))

    module = load_module(config_path)
    raw = getattr(module, "SITE", None)
    if raw is None and hasattr(module, "build"):
        return SiteConfig(
            root=root,
            package_root=PACKAGE_ROOT,
            output=root / "public",
            static=root / "static",
            pages=[PageSpec(config_path, root / "public")],
        )

    if not isinstance(raw, dict):
        raise RuntimeError(
            f"{config_path} must define SITE as a dict or build() for a single-page site"
        )

    output = root / raw.get("output", "public")
    static_value = raw.get("static", "static")
    static = root / static_value if static_value else None
    pages = [
        PageSpec(root / source, output / target)
        for source, target in raw.get("pages", [])
    ]

    return SiteConfig(root=root, package_root=PACKAGE_ROOT, output=output, static=static, pages=pages)


def resolve_config_path(path: str | Path | None) -> Path:
    if path:
        config_path = Path(path).resolve()
        if not config_path.exists():
            raise RuntimeError(f"Config or page file does not exist: {config_path}")
        return config_path

    cwd = Path.cwd().resolve()
    for name in ("site.py", "index.py"):
        candidate = cwd / name
        if candidate.exists():
            return candidate

    raise RuntimeError(
        f"No site.py or index.py found in {cwd}. Run `pysitegen init .` to create a starter site."
    )


def init_project(path: Path) -> None:
    root = path.resolve()
    root.mkdir(parents=True, exist_ok=True)

    files = {
        root / "index.py": STARTER_INDEX,
        root / "assets" / "index.css": STARTER_CSS,
        root / "content" / "docs" / ".gitkeep": "",
        root / ".gitignore": STARTER_GITIGNORE,
        root / "README.md": STARTER_README,
    }

    static_dir = root / "static"
    static_dir.mkdir(parents=True, exist_ok=True)
    files[root / "static" / "robots.txt"] = "User-agent: *\nAllow: /\n"

    for target, content in files.items():
        write_starter_file(target, content)

    favicon_source = PACKAGE_ROOT / "static" / "favicon.png"
    favicon_target = static_dir / "favicon.png"
    if favicon_source.exists():
        copy_starter_file(favicon_source, favicon_target)

    relative = root if root == Path.cwd().resolve() else root
    print(f"Created pysitegen site at {relative}")
    print("Next steps:")
    print(f'  Set-Location "{root}"')
    print("  pysitegen serve")


def write_starter_file(path: Path, content: str) -> None:
    if path.exists():
        raise RuntimeError(f"Refusing to overwrite existing file: {path}")

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def copy_starter_file(source: Path, target: Path) -> None:
    if target.exists():
        raise RuntimeError(f"Refusing to overwrite existing file: {target}")

    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(source, target)


def build(config: SiteConfig) -> None:
    clean_output(config)
    copy_static(config)

    try:
        for page in config.pages:
            document = build_document(page.source)
            html_path = render_site(document, page.output)
            print(f"Generated {html_path.relative_to(config.root)}")
    finally:
        clean_pycache([config.root, config.package_root])


def compile_project(paths: Iterable[str | Path] = ()) -> None:
    compile_paths = resolve_compile_paths(paths)
    cleanup_roots = [path if path.is_dir() else path.parent for path in compile_paths]
    ok = True

    try:
        for path in compile_paths:
            if not path.exists():
                raise RuntimeError(f"Compile path does not exist: {path}")

            if path.is_dir():
                ok = compileall.compile_dir(path, quiet=1) and ok
                continue

            if path.suffix == ".py":
                ok = compileall.compile_file(path, quiet=1) and ok
                continue

            raise RuntimeError(f"Compile path must be a Python file or directory: {path}")

        if not ok:
            raise RuntimeError("Compile check failed")

        rendered_paths = ", ".join(str(path) for path in compile_paths)
        print(f"Compiled {rendered_paths}")
    finally:
        clean_pycache(cleanup_roots)


def resolve_compile_paths(paths: Iterable[str | Path]) -> list[Path]:
    explicit = [Path(path).resolve() for path in paths]
    if explicit:
        return explicit

    cwd = Path.cwd().resolve()
    site_paths = [path for path in [*cwd.glob("*.py"), cwd / "pages"] if path.exists()]
    if site_paths:
        return site_paths

    repo_paths = [path for path in [cwd / "src", cwd / "website"] if path.exists()]
    if repo_paths:
        return repo_paths

    return [cwd]


def build_document(page_path: Path) -> Document:
    if not page_path.exists():
        raise RuntimeError(f"Configured page does not exist: {page_path}")

    module = load_module(page_path)
    if not hasattr(module, "build"):
        raise RuntimeError(f"{page_path} must define build()")

    document = module.build()
    if not isinstance(document, Document):
        raise RuntimeError(f"{page_path} build() must return pysitegen.Document")

    return document


def clean_output(config: SiteConfig) -> None:
    resolved_output = config.output.resolve()
    resolved_root = config.root.resolve()

    if resolved_output.parent != resolved_root:
        raise RuntimeError(f"Refusing to clean unexpected output path: {resolved_output}")

    if resolved_output.exists():
        shutil.rmtree(resolved_output)

    resolved_output.mkdir(parents=True, exist_ok=True)


def copy_static(config: SiteConfig) -> None:
    if not config.static or not config.static.exists():
        return

    copy_tree_contents(config.static, config.output)


def clean_pycache(paths: Iterable[Path]) -> None:
    seen: set[Path] = set()

    for path in paths:
        root = path.resolve()
        if root in seen or not root.exists():
            continue

        seen.add(root)

        for cache_dir in root.rglob("__pycache__"):
            resolved_cache = cache_dir.resolve()

            if resolved_cache == root or root not in resolved_cache.parents:
                raise RuntimeError(f"Refusing to clean unexpected pycache path: {resolved_cache}")

            if cache_dir.is_dir():
                shutil.rmtree(cache_dir)


def copy_tree_contents(source: Path, target: Path) -> None:
    for item in source.rglob("*"):
        if any(part.startswith(".") for part in item.relative_to(source).parts):
            continue

        relative = item.relative_to(source)
        destination = target / relative

        if item.is_dir():
            destination.mkdir(parents=True, exist_ok=True)
            continue

        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(item, destination)

class PySiteGenHTTPServer(http.server.ThreadingHTTPServer):
    allow_reuse_address = True
    daemon_threads = True

def serve(directory: Path, host: str, port: int) -> None:
    handler = partial(http.server.SimpleHTTPRequestHandler, directory=str(directory))

    with PySiteGenHTTPServer((host, port), handler) as server:
        print(f"Serving {directory} at http://{host}:{port}/")
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            print("\nStopped server.")
        finally:
            server.shutdown()
            server.server_close()


def load_module(path: Path) -> ModuleType:
    spec = importlib.util.spec_from_file_location(path.stem, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Could not load {path}")

    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


if __name__ == "__main__":
    main()
