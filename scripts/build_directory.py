#!/usr/bin/env python3
"""Builds the directory landing page and per-tool detail pages from data."""

import csv
import html
import re
import shutil
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[1]
DATA_CSV = ROOT / "data" / "tools.csv"
TEMPLATE_DIR = ROOT / "templates" / "directory"
INDEX_TEMPLATE = TEMPLATE_DIR / "index.html.tmpl"
DETAIL_TEMPLATE = TEMPLATE_DIR / "detail.html.tmpl"
OUTPUT_DIR = ROOT / "interpolations" / "directory"
ASSET_DIR = OUTPUT_DIR / "assets"
LOGO_DIR = ASSET_DIR / "logos"
BG_WEBP_DIR = ASSET_DIR / "bg" / "webp"
BG_PNG_DIR = ASSET_DIR / "bg" / "png"

BACKGROUND_BASES = sorted({p.stem.rsplit('-', 1)[0] for p in BG_WEBP_DIR.glob('bg-still-*-550.webp')})
BACKGROUND_BASES = [b for b in BACKGROUND_BASES if b != 'bg-still-test']
if not BACKGROUND_BASES:
    raise SystemExit('No background assets found.')

CATEGORY_ORDER = [
    "Multi-Tool Platform",
    "Image Generator",
    "Video Generator",
    "Upscaler",
    "Discovery",
    "Music and Audio",
    "Image Editor",
    "Image and Video Generator",
    "Conversational AI",
    "Embedded AI",
]

LOGO_OVERRIDES = {
    "Adobe Firefly": "firefly",
    "Canva Magic Studio": "canva",
    "Canva AI": "canva",
    "Topaz AI": "topazlabs",
    "Figma AI": "figma",
    "Photoshop AI": "photoshop",
    "Claude": "cluade",
    "Perplexity AI": "perplexity",
}



def slugify(value: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", value.lower())
    slug = slug.strip("-")
    return slug or "tool"


def determine_logo_base(name: str) -> str | None:
    override = LOGO_OVERRIDES.get(name)
    if override is False:  # explicit skip
        return None
    if override:
        base = override
    else:
        base = re.sub(r"[^a-z0-9]", "", name.lower())
    if not base:
        return None
    candidate = LOGO_DIR / f"{base}-logo-white.png"
    if candidate.exists():
        return base
    return None


def format_filter_buttons(categories: list[str]) -> str:
    ordered: list[str] = []
    for label in CATEGORY_ORDER:
        if label in categories:
            ordered.append(label)
    for label in categories:
        if label not in ordered:
            ordered.append(label)
    parts = []
    parts.append(
        "<button\n"
        "                            class=\"filter-btn is-active\"\n"
        "                            data-filter=\"All\"\n"
        "                            aria-pressed=\"true\"\n"
        "                        >\n"
        "                            All\n"
        "                        </button>"
    )
    for label in ordered:
        parts.append(
            "<button\n"
            "                            class=\"filter-btn\"\n"
            f"                            data-filter=\"{html.escape(label)}\"\n"
            "                            aria-pressed=\"false\"\n"
            "                        >\n"
            f"                            {html.escape(label)}\n"
            "                        </button>"
        )
    return "\n".join(parts)


def indent(text: str, spaces: int) -> str:
    prefix = " " * spaces
    return "\n".join(f"{prefix}{line}" if line else "" for line in text.splitlines())


def read_tools() -> list[dict]:
    if not DATA_CSV.exists():
        raise SystemExit(f"Data file not found: {DATA_CSV}")
    tools: list[dict] = []
    with DATA_CSV.open(newline="", encoding="utf-8") as fh:
        reader = csv.DictReader(fh)
        for row in reader:
            name = row["name"].strip()
            if not name:
                continue
            features = [row.get(f"feature_{i}", "").strip() for i in range(1, 4)]
            features = [f for f in features if f]
            url = row.get("website", "").strip()
            short_desc = row.get("short_description", "").strip()
            category = row.get("category", "").strip() or "Embedded AI"
            tools.append(
                {
                    "name": name,
                    "slug": slugify(name),
                    "category": category,
                    "short_description": short_desc,
                    "features": features,
                    "url": url,
                }
            )
    return tools


def ensure_background(index: int) -> str:
    base = BACKGROUND_BASES[index % len(BACKGROUND_BASES)]
    webp_expected = BG_WEBP_DIR / f"{base}-550.webp"
    png_expected = BG_PNG_DIR / f"{base}.png"
    if not webp_expected.exists():
        raise SystemExit(f"Background asset missing: {webp_expected}")
    if not png_expected.exists():
        raise SystemExit(f"Background asset missing: {png_expected}")
    return base


def build_card(tool: dict, background_base: str, logo_base: str | None) -> str:
    logo_html = ""
    if logo_base:
        logo_html = (
            "<img\n"
            "                                    class=\"tool-card__logo\"\n"
            f"                                    src=\"assets/logos/{logo_base}-logo-white.png\"\n"
            f"                                    alt=\"{html.escape(tool['name'])} logo\"\n"
            "                                />"
        )
    return (
        "<article\n"
        f"                        class=\"tool-card tool-card--detailed\"\n"
        f"                        aria-label=\"{html.escape(tool['name'])}\"\n"
        f"                        data-category=\"{html.escape(tool['category'])}\"\n"
        f"                        data-tags=\"{html.escape(tool['category'])}\"\n"
        "                    >\n"
        "                        <a\n"
        "                            class=\"tool-card__link\"\n"
        f"                            href=\"./{html.escape(tool['slug'])}/\"\n"
        "                        >\n"
        "                            <div class=\"tool-card__media\">\n"
        "                                <img\n"
        "                                    class=\"tool-card__bg__still\"\n"
        f"                                    src=\"assets/bg/webp/{background_base}-550.webp\"\n"
        f"                                    srcset=\"assets/bg/webp/{background_base}-275.webp   275w,\n"
        f"                                        assets/bg/webp/{background_base}-550.webp   550w,\n"
        f"                                        assets/bg/webp/{background_base}-1100.webp 1100w\"\n"
        "                                    sizes=\"(max-width: 768px) 100vw, (min-width: 1024px) 33vw, 50vw\"\n"
        "                                    alt=\"\"\n"
        "                                    aria-hidden=\"true\"\n"
        "                                />\n"
        f"{indent(logo_html, 32) if logo_html else ''}\n"
        "                            </div>\n"
        "                            <div class=\"tool-card__content\">\n"
        f"                                <span class=\"pill\">{html.escape(tool['category'])}</span>\n"
        f"                                <h3 class=\"tool-card__title\">{html.escape(tool['name'])}</h3>\n"
        f"                                <p class=\"tool-card__desc\">{html.escape(tool['short_description'])}</p>\n"
        "                            </div>\n"
        "                        </a>\n"
        "                    </article>"
    )


def format_feature_list(features: list[str]) -> str:
    if not features:
        return ""
    return "\n".join(
        "            <li>" + html.escape(feature) + "</li>" for feature in features
    )


def build_media_logo(tool: dict, logo_base: str | None) -> str:
    if not logo_base:
        return ""
    return (
        "            <img\n"
        "              class=\"detail__media-logo\"\n"
        f"              src=\"../assets/logos/{logo_base}-logo-white.png\"\n"
        f"              alt=\"{html.escape(tool['name'])} logo\"\n"
        "              width=\"420\"\n"
        "              height=\"220\"\n"
        "              decoding=\"async\"\n"
        "            />"
    )


def build_detail_page(tool: dict, background_base: str, logo_base: str | None, template: str) -> str:
    parsed = urlparse(tool["url"])
    domain = parsed.netloc or tool["url"].replace("https://", "").replace("http://", "")
    domain = domain.rstrip("/")
    replacements = {
        "{{ TOOL_NAME }}": html.escape(tool["name"]),
        "{{ META_DESCRIPTION }}": html.escape(f"{tool['name']} — {tool['short_description']}") if tool["short_description"] else html.escape(tool["name"]),
        "{{ DETAIL_BACKGROUND }}": f"../assets/bg/png/{background_base}.png",
        "{{ MEDIA_LOGO }}": build_media_logo(tool, logo_base),
        "{{ SHORT_DESCRIPTION }}": html.escape(tool["short_description"]),
        "{{ FEATURE_LIST }}": format_feature_list(tool["features"]),
        "{{ TOOL_URL }}": html.escape(tool["url"] or "#"),
        "{{ TOOL_DOMAIN }}": html.escape(domain),
    }
    html_text = template
    for key, value in replacements.items():
        html_text = html_text.replace(key, value)
    return html_text


def write_index(tools: list[dict]) -> None:
    template = INDEX_TEMPLATE.read_text(encoding="utf-8")
    categories = sorted({tool["category"] for tool in tools})
    filters_html = format_filter_buttons(categories)
    cards = []
    for idx, tool in enumerate(tools):
        background = ensure_background(idx % 45)
        logo_base = determine_logo_base(tool["name"])
        cards.append(build_card(tool, background, logo_base))
        tool["_background"] = background
        tool["_logo_base"] = logo_base
    cards_html = "\n\n".join(cards)
    rendered = template.replace("{{ FILTER_BUTTONS }}", indent(filters_html, 24))
    rendered = rendered.replace("{{ TOOL_CARDS }}", indent(cards_html, 20))
    (OUTPUT_DIR / "index.html").write_text(rendered, encoding="utf-8")


def clean_detail_directories() -> None:
    for path in OUTPUT_DIR.iterdir():
        if path.is_dir() and path.name not in {"assets"}:
            shutil.rmtree(path)


def write_detail_pages(tools: list[dict]) -> None:
    template = DETAIL_TEMPLATE.read_text(encoding="utf-8")
    for tool in tools:
        slug = tool["slug"]
        background = tool.get("_background")
        logo_base = tool.get("_logo_base")
        html_text = build_detail_page(tool, background, logo_base, template)
        dest_dir = OUTPUT_DIR / slug
        dest_dir.mkdir(parents=True, exist_ok=True)
        (dest_dir / "index.html").write_text(html_text, encoding="utf-8")


def main() -> None:
    tools = read_tools()
    if not tools:
        raise SystemExit("No tools found in data.")
    clean_detail_directories()
    write_index(tools)
    write_detail_pages(tools)
    print(f"Generated {len(tools)} tools.")


if __name__ == "__main__":
    main()
