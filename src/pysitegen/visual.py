from __future__ import annotations

import json
from typing import Any, Mapping, cast

from . import components as _components
from .behaviors import Behavior
from .components import Node
from .elements import canvas, tag


SUBSTRATE_RUNTIME_URL = "https://cdn.ujjwalvivek.com/scripts/substrate/latest/main.js"
LayerSpec = str | tuple[str, Mapping[str, Any]]
Scene = list[dict[str, Any]]


def visual_scene(*layers: LayerSpec) -> Scene:
    return [normalize_layer(layer) for layer in layers]


def visual_canvas(
    scene: Scene,
    *,
    id: str,
    fps: int = 0,
    palette: Mapping[str, str] | None = None,
    **attrs: str | int | float | bool | None,
) -> Node:
    data_attrs: dict[str, str | int | float | bool | None] = {
        "id": id,
        "data_pysitegen_canvas": True,
        "data_scene": json.dumps(scene, separators=(",", ":")),
        "data_fps": fps,
        **attrs,
    }

    if palette:
        data_attrs["data_palette"] = json.dumps(dict(palette), separators=(",", ":"))

    return canvas(**data_attrs)


def canvas_background(runtime: str = SUBSTRATE_RUNTIME_URL) -> Behavior:
    return Behavior(
        head=[
            tag(
                "script",
                raw_html(canvas_adapter(runtime)),
                type="module",
            )
        ],
    )


def normalize_layer(layer: LayerSpec) -> dict[str, Any]:
    if isinstance(layer, str):
        return {"primitive": layer, "options": {}}

    primitive, options = layer
    return {"primitive": primitive, "options": dict(options)}


def canvas_adapter(runtime: str) -> str:
    runtime_json = json.dumps(runtime)
    return f"""
import {{ compose, primitives }} from {runtime_json};

const DEFAULT_PALETTE = {{
  primary: "#ffb057",
  secondary: "#cfc4b4",
  accent: "#ff7a59",
  background: "#0b0b0a",
}};

function readJson(value, fallback) {{
  try {{
    return value ? JSON.parse(value) : fallback;
  }} catch {{
    return fallback;
  }}
}}

function cssColor(styles, name, fallback) {{
  return styles.getPropertyValue(name).trim() || fallback;
}}

function paletteFor(canvas) {{
  const configured = readJson(canvas.dataset.palette, null);
  if (configured) return {{ ...DEFAULT_PALETTE, ...configured }};

  const styles = getComputedStyle(document.documentElement);
  return {{
    primary: cssColor(styles, "--accent", DEFAULT_PALETTE.primary),
    secondary: cssColor(styles, "--soft", DEFAULT_PALETTE.secondary),
    accent: cssColor(styles, "--accent-strong", DEFAULT_PALETTE.accent),
    background: cssColor(styles, "--bg", DEFAULT_PALETTE.background),
  }};
}}

function sceneFor(canvas) {{
  return readJson(canvas.dataset.scene, [])
    .map((layer) => ({{
      fn: primitives[layer.primitive],
      options: layer.options ?? {{}},
    }}))
    .filter((layer) => typeof layer.fn === "function");
}}

function resize(canvas, ctx, render, palette, options, time = 0) {{
  const parent = canvas.parentElement ?? document.body;
  const dpr = window.devicePixelRatio || 1;
  const width = Math.max(1, parent.clientWidth || window.innerWidth);
  const height = Math.max(1, parent.clientHeight || window.innerHeight);
  canvas.style.width = `${{width}}px`;
  canvas.style.height = `${{height}}px`;
  canvas.width = Math.round(width * dpr);
  canvas.height = Math.round(height * dpr);
  ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
  ctx.clearRect(0, 0, width, height);
  render(ctx, width, height, time, palette, options);
}}

function bindCanvas(canvas) {{
  const scene = sceneFor(canvas);
  if (!scene.length) return;

  const ctx = canvas.getContext("2d");
  if (!ctx) return;

  const render = compose(scene);
  const palette = paletteFor(canvas);
  const fps = Number(canvas.dataset.fps ?? 0);
  const reduced = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  const effectiveFps = reduced ? 0 : Math.max(0, fps);
  const options = {{ fps: effectiveFps }};
  const interval = effectiveFps > 0 ? 1000 / effectiveFps : Infinity;
  let frame = 0;
  let last = 0;

  const draw = (time) => {{
    const width = parseInt(canvas.style.width, 10) || canvas.width;
    const height = parseInt(canvas.style.height, 10) || canvas.height;
    ctx.clearRect(0, 0, width, height);
    render(ctx, width, height, time / 1000, palette, options);
  }};

  const observer =
    typeof ResizeObserver !== "undefined"
      ? new ResizeObserver(() => resize(canvas, ctx, render, palette, options))
      : null;
  observer?.observe(canvas.parentElement ?? document.body);
  resize(canvas, ctx, render, palette, options);

  if (effectiveFps === 0) return;

  const tick = (time) => {{
    frame = requestAnimationFrame(tick);
    if (document.hidden) return;
    if (time - last < interval) return;
    last = time;
    draw(time);
  }};

  frame = requestAnimationFrame(tick);
  window.addEventListener("beforeunload", () => cancelAnimationFrame(frame), {{ once: true }});
}}

document.querySelectorAll("[data-pysitegen-canvas]").forEach(bindCanvas);
""".strip()


def raw_html(html: str) -> Any:
    return cast(Any, getattr(_components, "RawHtml"))(html)
