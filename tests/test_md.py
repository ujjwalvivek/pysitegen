from __future__ import annotations

from pysitegen import markdown_text, markdown_toc


def render_markdown(markdown: str) -> str:
    document = markdown_text(markdown)
    return "\n".join(node.render() for node in document.nodes)


def test_python_code_block_is_highlighted_and_escaped() -> None:
    html = render_markdown(
        '''```python
from pysitegen import page
value = "<script>"
# comment
def build():
    return page(title="Demo")
```'''
    )

    assert 'class="language-python has-highlight"' in html
    assert '<span class="tok-keyword">from</span>' in html
    assert '<span class="tok-string">"&lt;script&gt;"</span>' in html
    assert '<span class="tok-comment"># comment</span>' in html
    assert '<span class="tok-call">page</span>' in html
    assert "<script>" not in html


def test_bash_code_block_is_highlighted() -> None:
    html = render_markdown(
        '''```bash
pysitegen serve --host 127.0.0.1
```'''
    )

    assert 'class="language-bash has-highlight"' in html
    assert '<span class="tok-command">pysitegen</span>' in html
    assert '<span class="tok-option">--host</span>' in html


def test_unknown_code_block_stays_escaped_without_highlight() -> None:
    html = render_markdown(
        '''```custom
<unsafe>
```'''
    )

    assert 'class="language-custom"' in html
    assert "has-highlight" not in html
    assert "&lt;unsafe&gt;" in html
    assert "<unsafe>" not in html


def test_markdown_toc_can_render_collapsible_details() -> None:
    document = markdown_text(
        """# Title

## Install

### Options
"""
    )

    html = markdown_toc(document, collapsible=True).render()

    assert '<aside class="docs-toc collapsible">' in html
    assert 'class="eyebrow docs-toc-desktop-title"' in html
    assert 'class="docs-toc-list docs-toc-desktop-list"' in html
    assert '<details class="docs-toc-details">' in html
    assert '<summary class="docs-toc-summary">On this page</summary>' in html
    assert 'class="docs-toc-list docs-toc-mobile-list"' in html
    assert 'href="#install"' in html
    assert 'href="#options"' in html


def test_markdown_toc_open_flag_sets_details_open() -> None:
    document = markdown_text("## Install\n")

    html = markdown_toc(document, collapsible=True, open=True).render()

    assert '<details class="docs-toc-details" open>' in html
