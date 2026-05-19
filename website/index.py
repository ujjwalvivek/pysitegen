import inspect
from pathlib import Path

from pysitegen import (
    a,
    article,
    asset,
    button,
    canvas_background,
    default_dark,
    div,
    footer,
    h1,
    h2,
    main,
    markdown_file,
    markdown_toc,
    nav,
    p,
    page,
    section,
    spa,
    tag,
    visual_canvas,
    visual_scene,
)
from pysitegen.md import highlight_code

ROOT = Path(__file__).resolve().parent
ASSETS = ROOT / "assets"
GITHUB_BADGE = "https://echopoint.ujjwalvivek.com/svg/badges/custom?bg=111111&badgeColor=655317&textColor=e8e8e8&border=FFD43B&borderWidth=2&rx=0&px=0&py=0&leftText=code&rightText=MIT&logo=github"


def route_link(route: str, label: str, active: bool = False):
    return a(
        label,
        href=f"#{route}",
        class_="site-link" + (" active" if active else ""),
        data_route=route,
    )


def route_panel(route: str, *children, active: bool = False):
    return section(
        *children,
        id=route,
        class_="site-route" + (" active" if active else ""),
        data_route_panel=route,
    )


def svg_icon(kind: str, class_name: str):
    if kind == "copy":
        return tag(
            "svg",
            tag(
                "rect",
                x="9",
                y="9",
                width="10",
                height="10",
                rx="0",
                class_="copy-back",
            ),
            tag(
                "rect",
                x="5",
                y="5",
                width="10",
                height="10",
                rx="0",
                class_="copy-front",
            ),
            tag("path", d="M7 10.5l2.2 2.2L14 7.8", class_="copy-check"),
            viewBox="0 0 24 24",
            aria_hidden="true",
            class_=class_name,
        )

    if kind == "files":
        return tag(
            "svg",
            tag("path", d="M6 4h7l4 4v12H6z"),
            tag("path", d="M13 4v5h4"),
            tag("path", d="M8.5 13h6"),
            tag("path", d="M8.5 16h4"),
            viewBox="0 0 24 24",
            aria_hidden="true",
            class_=class_name,
        )

    if kind == "document":
        return tag(
            "svg",
            tag("path", d="M5 5h14v14H5z"),
            tag("path", d="M8 9h8"),
            tag("path", d="M8 12h8"),
            tag("path", d="M8 15h5"),
            viewBox="0 0 24 24",
            aria_hidden="true",
            class_=class_name,
        )

    return tag(
        "svg",
        tag("path", d="M4 12h16"),
        tag("path", d="M12 4v16"),
        tag("path", d="M7 7l10 10"),
        tag("path", d="M17 7L7 17"),
        viewBox="0 0 24 24",
        aria_hidden="true",
        class_=class_name,
    )


DEMO_IMPORTS = (
    "from pysitegen import default_dark, div, h1, main, p, page, section, tag"
)


def demo_build():
    return page(
        section(
            div(
                h2("recursion is"),
                h1("COOL"),
                p(
                    "Here's the copy of links again, in case you missed it the first time.",
                    class_="site-hero-copy",
                ),
                div(
                    a(
                        tag(
                            "img",
                            src=GITHUB_BADGE,
                            alt="GitHub code MIT",
                            class_="github-badge",
                        ),
                        href="https://github.com/ujjwalvivek/pysitegen",
                        class_="github-link",
                        target="_blank",
                        rel="noreferrer",
                    ),
                    p("pysitegen 0.1.0", class_="eyebrow"),
                    class_="hero-meta",
                ),
                div(
                    div(
                        tag(
                            "code",
                            "pip install pysitegen",
                            class_="install-command",
                        ),
                        button(
                            svg_icon("copy", "copy-svg"),
                            class_="copy-button",
                            type="button",
                            data_copy_text="pip install pysitegen",
                            aria_label="Copy install command",
                            title="Copy install command",
                        ),
                        class_="install-shell",
                    ),
                    a(
                        "Read Docs",
                        href="#docs",
                        class_="button primary",
                        data_route="docs",
                    ),
                    class_="hero-actions",
                ),
                class_="hero-copy stack",
            ),
            class_="hero-bottom",
        ),
        title="Site",
        theme=default_dark(),
    )


def demo_code():
    source = inspect.getsource(demo_build).replace(
        "def demo_build():", "def build():", 1
    )
    return f"{DEMO_IMPORTS}\n\n{source}".strip()


def demo_document():
    return demo_build()


def preview_pane(rendered):
    return div(
        tag(
            "div",
            p("public/index.html", class_="panel-title"),
            div(
                button(
                    "Preview",
                    class_="panel-switch active",
                    type="button",
                    data_demo_toggle="preview",
                    aria_pressed="true",
                ),
                button(
                    "HTML",
                    class_="panel-switch",
                    type="button",
                    data_demo_toggle="html",
                    aria_pressed="false",
                ),
                class_="panel-switches",
            ),
            class_="panel-label split-label",
        ),
        div(
            div(
                rendered.body,
                class_="preview-surface demo-panel active",
                data_demo_panel="preview",
            ),
            tag(
                "pre",
                tag("code", rendered.render().strip()),
                class_="generated-html demo-panel",
                data_demo_panel="html",
                hidden=True,
            ),
            class_="output-stage",
        ),
        class_="preview-pane",
    )


def workbench():
    rendered = demo_document()
    return div(
        div(
            tag(
                "div",
                p("index.py", class_="panel-title"),
                a("Read the DOCS", href="#docs", data_route="docs"),
                class_="panel-label split-label",
            ),
            tag(
                "pre",
                tag(
                    "code",
                    highlight_code(demo_code(), "python"),
                    class_="language-python has-highlight",
                ),
                class_="hero-code",
            ),
            class_="code-pane",
        ),
        preview_pane(rendered),
        class_="workbench",
    )


def calm_wallpaper():
    scene = visual_scene(
        (
            "background",
            {
                "colorStops": [
                    [0, "primary", "20"],
                    [0.2, "accent", "08"],
                    [1, "primary", "00"],
                ],
            },
        ),
        (
            "particles",
            {
                "density": 1.0,
                "opacity": 0.5,
                "minRadius": 200,
                "maxRadius": 1200,
                "speed": 0.05,
            },
        ),
        (
            "scanlines",
            {
                "density": 1,
                "opacity": 1,
                "speed": 0.5,
            },
        ),
        (
            "streams",
            {
                "density": 2,
                "opacity": 0.85,
                "speed": 0.1,
            },
        ),
        ("vignette", {"opacity": 0.9, "innerRadius": 0.2, "outerRadius": 0.92}),
    )
    return visual_canvas(
        scene,
        id="site-wallpaper",
        fps=30,
        class_="site-wallpaper",
        aria_hidden=True,
        palette={
            "primary": "#306998",
            "secondary": "#FFD43B",
            "accent": "#FFE873",
            "background": "#0a0a0a",
        },
    )


def home():
    return route_panel(
        "home",
        section(
            section(
                div(
                    h2("build websites in"),
                    h1("PYTHON"),
                    p(
                        "A small build tool for Python-authored pages without a runtime server or a client framework. This website is built with pysitegen.",
                        class_="site-hero-copy",
                    ),
                    div(
                        a(
                            tag(
                                "img",
                                src=GITHUB_BADGE,
                                alt="GitHub code MIT",
                                class_="github-badge",
                            ),
                            href="https://github.com/ujjwalvivek/pysitegen",
                            class_="github-link",
                            target="_blank",
                            rel="noreferrer",
                        ),
                        p("pysitegen 0.1.0", class_="eyebrow"),
                        class_="hero-meta",
                    ),
                    div(
                        div(
                            tag(
                                "code",
                                "pip install pysitegen",
                                class_="install-command",
                            ),
                            button(
                                svg_icon("copy", "copy-svg"),
                                class_="copy-button",
                                type="button",
                                data_copy_text="pip install pysitegen",
                                aria_label="Copy install command",
                                title="Copy install command",
                            ),
                            class_="install-shell",
                        ),
                        a(
                            "<Read_Docs/>",
                            href="#docs",
                            class_="button primary",
                            data_route="docs",
                        ),
                        class_="hero-actions",
                    ),
                    class_="hero-copy stack",
                ),
                class_="hero-bottom",
            ),
            workbench(),
            class_="site-hero",
        ),
        active=True,
    )


def docs():
    doc = markdown_file(ROOT / "content" / "docs" / "getting-started.md")
    return route_panel(
        "docs",
        div(
            markdown_toc(doc, collapsible=True),
            article(doc.nodes, class_="docs-content"),
            class_="docs-layout",
        ),
    )


def build():
    return page(
        div(
            calm_wallpaper(),
            div(
                nav(
                    a("P Y S I T E G E N", href="#home", class_="brand"),
                    div(
                        route_link("home", "Home", True),
                        route_link("docs", "Docs"),
                        class_="cluster site-links",
                    ),
                    class_="container site-nav-inner",
                ),
                class_="site-nav-shell",
                data_sticky_nav=True,
            ),
            main(home(), docs(), class_="container site-main"),
            footer(class_="site-footer"),
            class_="pysitegen-site",
        ),
        title="PySiteGen - Tiny Python Static Site Generator",
        description="Python-authored static sites with terminal-styled primitives.",
        head=[tag("link", rel="icon", type="image/png", href="/favicon.png")],
        theme=default_dark(),
        behaviors=[spa(), canvas_background()],
        assets=[
            asset(ASSETS / "index.css", "assets/index.css"),
            asset(ASSETS / "index.js", "assets/index.js"),
        ],
        stylesheets=["assets/index.css"],
        scripts=["assets/index.js"],
    )
