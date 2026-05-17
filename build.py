#!/usr/bin/env python3
"""
build.py — Regenerate website/index.html from src/template.html + data/*.yaml
"""

import re
import sys
import subprocess
import html
from pathlib import Path

# ──────────────────────────────────────────────────────────────────────────────
# Auto-install pyyaml if missing
# ──────────────────────────────────────────────────────────────────────────────
try:
    import yaml
except ImportError:
    print("  Installing pyyaml...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "pyyaml", "-q"])
    import yaml

# ──────────────────────────────────────────────────────────────────────────────
# Paths
# ──────────────────────────────────────────────────────────────────────────────
BASE_DIR = Path(__file__).parent
TEMPLATE = BASE_DIR / "src" / "template.html"
DATA_DIR = BASE_DIR / "data"
OUTPUT   = BASE_DIR / "website" / "index.html"

# ──────────────────────────────────────────────────────────────────────────────
# SVG Icons keyed by feature id
# ──────────────────────────────────────────────────────────────────────────────
FEATURE_SVGS = {
    "website_builder": """<svg class="feat-icon" viewBox="0 0 52 52" fill="none">
                <rect x="4" y="9" width="44" height="34" rx="4" stroke="rgba(240,165,0,0.35)" stroke-width="1.5"/>
                <rect x="4" y="9" width="44" height="9" rx="4" fill="rgba(240,165,0,0.08)" stroke="rgba(240,165,0,0.35)" stroke-width="1.5"/>
                <circle cx="12" cy="13.5" r="2" fill="#F0A500"/>
                <circle cx="20" cy="13.5" r="2" fill="rgba(240,165,0,0.35)"/>
                <circle cx="28" cy="13.5" r="2" fill="rgba(240,165,0,0.15)"/>
                <rect x="12" y="24" width="28" height="2.5" rx="1.25" fill="rgba(240,165,0,0.25)"/>
                <rect x="12" y="30" width="18" height="2" rx="1" fill="rgba(240,165,0,0.15)"/>
                <rect x="12" y="35" width="22" height="2" rx="1" fill="rgba(240,165,0,0.1)"/>
            </svg>""",

    "analytics": """<svg class="feat-icon" viewBox="0 0 52 52" fill="none">
                <path d="M8 40L20 26L30 33L42 17" stroke="rgba(240,165,0,0.4)" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
                <circle cx="20" cy="26" r="3" fill="#F0A500"/>
                <circle cx="30" cy="33" r="3" fill="rgba(240,165,0,0.55)"/>
                <circle cx="42" cy="17" r="3" fill="rgba(240,165,0,0.35)"/>
                <rect x="8" y="42" width="36" height="1.5" rx="0.75" fill="rgba(240,165,0,0.15)"/>
                <rect x="8" y="8" width="1.5" height="32" rx="0.75" fill="rgba(240,165,0,0.15)"/>
            </svg>""",

    "link_in_bio": """<svg class="feat-icon" viewBox="0 0 52 52" fill="none">
                <rect x="15" y="6" width="22" height="40" rx="5" stroke="rgba(240,165,0,0.35)" stroke-width="1.5"/>
                <circle cx="26" cy="42" r="2" fill="rgba(240,165,0,0.35)"/>
                <rect x="19" y="14" width="14" height="2.5" rx="1.25" fill="#F0A500"/>
                <rect x="19" y="20" width="10" height="2" rx="1" fill="rgba(240,165,0,0.45)"/>
                <rect x="19" y="25" width="12" height="2" rx="1" fill="rgba(240,165,0,0.3)"/>
                <rect x="19" y="30" width="8" height="2" rx="1" fill="rgba(240,165,0,0.2)"/>
            </svg>""",

    "business_tools": """<svg class="feat-icon" viewBox="0 0 52 52" fill="none">
                <rect x="6" y="18" width="20" height="28" rx="3" stroke="rgba(240,165,0,0.35)" stroke-width="1.5"/>
                <rect x="30" y="6" width="16" height="16" rx="2" stroke="rgba(240,165,0,0.7)" stroke-width="1.5" fill="rgba(240,165,0,0.08)"/>
                <path d="M34 14h8M34 11h5" stroke="#F0A500" stroke-width="1.5" stroke-linecap="round"/>
                <rect x="30" y="28" width="16" height="2" rx="1" fill="rgba(240,165,0,0.3)"/>
                <rect x="30" y="33" width="12" height="2" rx="1" fill="rgba(240,165,0,0.2)"/>
                <rect x="30" y="38" width="14" height="2" rx="1" fill="rgba(240,165,0,0.15)"/>
                <rect x="10" y="22" width="12" height="10" rx="2" fill="rgba(240,165,0,0.08)" stroke="rgba(240,165,0,0.25)" stroke-width="1"/>
            </svg>""",
}

# Pricing check / cross SVGs
SVG_CHECK = '<svg width="15" height="15" viewBox="0 0 15 15" fill="none"><path d="M2.5 7.5l3.5 3.5 6-6" stroke="#F0A500" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/></svg>'
SVG_CROSS = '<svg width="15" height="15" viewBox="0 0 15 15" fill="none"><path d="M4 4l7 7M11 4l-7 7" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/></svg>'

# Arrow SVG for drawer nav
SVG_DRAWER_ARROW = '<svg class="drawer-arrow" width="14" height="14" viewBox="0 0 14 14" fill="none"><path d="M3 7h8M8 4l3 3-3 3" stroke="currentColor" stroke-width="1.3" stroke-linecap="round" stroke-linejoin="round"/></svg>'

# Hero arrow SVG
SVG_HERO_ARROW = '<svg width="15" height="15" viewBox="0 0 15 15" fill="none"><path d="M2.5 7.5h10M8.5 3.5l4 4-4 4" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/></svg>'

# Step arrow SVG
SVG_STEP_ARROW = '<svg width="10" height="10" viewBox="0 0 10 10" fill="none"><path d="M2 5h6M5 2l3 3-3 3" stroke="rgba(240,165,0,0.5)" stroke-width="1.2" stroke-linecap="round" stroke-linejoin="round"/></svg>'

# FAQ icon SVG (plus)
SVG_FAQ_ICON = '<svg width="10" height="10" viewBox="0 0 10 10" fill="none"><path d="M5 1v8M1 5h8" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/></svg>'

# Pricing badge dot SVG
SVG_PRICE_BADGE_DOT = '<svg width="8" height="8" viewBox="0 0 8 8" fill="#F0A500"><circle cx="4" cy="4" r="3"/></svg>'


# ──────────────────────────────────────────────────────────────────────────────
# Core inject function
# ──────────────────────────────────────────────────────────────────────────────
def inject(template: str, key: str, content: str) -> str:
    """Replace <!-- BUILD:key --> ... <!-- /BUILD:key --> with content."""
    pattern = rf"<!-- BUILD:{re.escape(key)} -->.*?<!-- /BUILD:{re.escape(key)} -->"
    replacement = f"<!-- BUILD:{key} -->\n{content}\n        <!-- /BUILD:{key} -->"
    result, count = re.subn(pattern, replacement, template, flags=re.DOTALL)
    if count == 0:
        print(f"  WARNING: BUILD:{key} not found in template")
    return result


# ──────────────────────────────────────────────────────────────────────────────
# Section renderers
# ──────────────────────────────────────────────────────────────────────────────

def render_nav_links(site: dict) -> str:
    nav = site.get("nav", {})
    links = nav.get("links", [])
    cta = nav.get("cta", {})
    lines = []
    for link in links:
        lines.append(f'        <li><a href="{html.escape(link["href"])}">{html.escape(link["label"])}</a></li>')
    if cta:
        lines.append(f'        <li><a href="{html.escape(cta["href"])}" class="nav-cta">{html.escape(cta["label"])}</a></li>')
    return "\n".join(lines)


def render_drawer_nav(site: dict) -> str:
    nav = site.get("nav", {})
    links = nav.get("links", [])
    lines = []
    for link in links:
        lines.append(
            f'        <li><a href="{html.escape(link["href"])}">\n'
            f'            {html.escape(link["label"])}\n'
            f'            {SVG_DRAWER_ARROW}\n'
            f'        </a></li>'
        )
    return "\n".join(lines)


def render_hero(site: dict) -> str:
    hero = site.get("hero", {})
    label = hero.get("label", "")
    headlines = hero.get("headline", [])
    sub = hero.get("sub", "")
    cta_primary = hero.get("cta_primary", "")
    cta_primary_href = hero.get("cta_primary_href", "#start")
    cta_secondary = hero.get("cta_secondary", "")
    cta_secondary_href = hero.get("cta_secondary_href", "#features")
    stats = hero.get("stats", [])

    # Build headline — join with <br>\n
    headline_html = "<br>\n        ".join(h for h in headlines)

    # Build stats HTML
    stats_html_parts = []
    for stat in stats:
        val = stat["value"]
        # Convert literal < to HTML entity for display
        val_display = val.replace("<", "&lt;")
        stats_html_parts.append(
            f'        <div class="stat">\n'
            f'            <div class="stat-val">{val_display}</div>\n'
            f'            <div class="stat-lbl">{html.escape(stat["label"])}</div>\n'
            f'        </div>'
        )
    stats_html = "\n".join(stats_html_parts)

    return f"""    <p class="hero-label">{html.escape(label).replace('—', '&mdash;')}</p>

    <h1 class="hero-headline">
        {headline_html}
    </h1>

    <p class="hero-sub">
        {html.escape(sub)}
    </p>

    <div class="hero-actions">
        <a href="{html.escape(cta_primary_href)}" class="btn-primary">
            {html.escape(cta_primary)}
            {SVG_HERO_ARROW}
        </a>
        <a href="{html.escape(cta_secondary_href)}" class="btn-ghost">{html.escape(cta_secondary)}</a>
    </div>

    <div class="hero-stats">
{stats_html}
    </div>"""


def render_features(features: dict) -> str:
    label = features.get("section_label", "")
    heading_raw = features.get("heading", "")
    # Convert \n to <br>
    heading_html = heading_raw.replace("\n", "<br>")
    sub = features.get("sub", "")
    items = features.get("items", [])

    delay_classes = ["", " d1", " d2", " d3"]

    # Build features-top
    top_html = f"""    <div class="features-top">
        <div class="reveal">
            <p class="sec-label">{html.escape(label)}</p>
            <h2 class="sec-heading">{heading_html}</h2>
        </div>
        <p class="sec-sub reveal d1">{html.escape(sub)}</p>
    </div>"""

    # Build features-grid
    cards_html_parts = []
    for i, item in enumerate(items):
        delay = delay_classes[i] if i < len(delay_classes) else ""
        feat_id = item.get("id", "")
        num_label = item.get("num_label", "")
        name = item.get("name", "")
        desc = item.get("desc", "")
        badge = item.get("badge", "")
        svg = FEATURE_SVGS.get(feat_id, "")

        card = f"""        <div class="feat-card reveal{delay}">
            <p class="feat-num">{html.escape(num_label).replace('—', '&mdash;')}</p>
            {svg}
            <h3 class="feat-name">{html.escape(name)}</h3>
            <p class="feat-desc">{html.escape(desc)}</p>
            <span class="feat-badge"><span class="feat-badge-dot"></span>{html.escape(badge)}</span>
        </div>"""
        cards_html_parts.append(card)

    grid_html = f"""    <div class="features-grid">

{chr(10).join(cards_html_parts)}

    </div>"""

    return top_html + "\n\n" + grid_html


def render_steps(steps: dict) -> str:
    label = steps.get("section_label", "")
    heading_raw = steps.get("heading", "")
    heading_html = heading_raw.replace("\n", "<br>")
    items = steps.get("items", [])

    delay_classes = ["", " d1", " d2"]

    steps_parts = []
    for i, item in enumerate(items):
        delay = delay_classes[i] if i < len(delay_classes) else ""
        num = item.get("num", "")
        title = item.get("title", "")
        desc = item.get("desc", "")
        is_last = (i == len(items) - 1)

        arrow_html = "" if is_last else f"""            <div class="step-arrow" aria-hidden="true">
                {SVG_STEP_ARROW}
            </div>
            """

        step = f"""        <div class="step reveal{delay}">
            {arrow_html}<div class="step-n">{html.escape(num)}</div>
            <h3 class="step-title">{html.escape(title)}</h3>
            <p class="step-desc">{html.escape(desc)}</p>
        </div>"""
        steps_parts.append(step)

    return f"""    <div class="reveal">
        <p class="sec-label">{html.escape(label)}</p>
        <h2 class="sec-heading">{heading_html}</h2>
    </div>

    <div class="steps">
{chr(10).join(steps_parts)}
    </div>"""


def render_testimonials(testimonials: dict) -> str:
    label = testimonials.get("section_label", "")
    heading_raw = testimonials.get("heading", "")
    heading_html = heading_raw.replace("\n", "<br>")
    sub = testimonials.get("sub", "")
    items = testimonials.get("items", [])

    delay_classes = ["", " d1", " d2"]

    top_html = f"""    <div class="proof-top">
        <div class="reveal">
            <p class="sec-label">{html.escape(label)}</p>
            <h2 class="sec-heading">{heading_html}</h2>
        </div>
        <p class="sec-sub reveal d1">
            {html.escape(sub)}
        </p>
    </div>"""

    cards_parts = []
    for i, item in enumerate(items):
        delay = delay_classes[i] if i < len(delay_classes) else ""
        quote = item.get("quote", "")
        name = item.get("name", "")
        role = item.get("role", "")
        initial = item.get("initial", name[0].upper() if name else "?")

        card = f"""        <div class="t-card reveal{delay}">
            <p class="t-quote">"{html.escape(quote)}"</p>
            <div class="t-author">
                <div class="t-avatar">{html.escape(initial)}</div>
                <div>
                    <div class="t-name">{html.escape(name)}</div>
                    <div class="t-role">{html.escape(role).replace('—', '&mdash;')}</div>
                </div>
            </div>
        </div>"""
        cards_parts.append(card)

    cards_html = f"""    <div class="cards-grid">
{chr(10).join(cards_parts)}
    </div>"""

    return top_html + "\n\n" + cards_html


def render_pricing(pricing: dict) -> str:
    label = pricing.get("section_label", "")
    heading_raw = pricing.get("heading", "")
    heading_html = heading_raw.replace("\n", "<br>")
    toggle_monthly = pricing.get("toggle_monthly", "Bulanan")
    toggle_annual = pricing.get("toggle_annual", "Tahunan")
    toggle_save = pricing.get("toggle_save", "2 bulan gratis")
    tiers = pricing.get("tiers", [])

    header_html = f"""    <div class="pricing-header reveal">
        <p class="sec-label">{html.escape(label)}</p>
        <h2 class="sec-heading">{heading_html}</h2>
        <div class="pricing-toggle" id="billingToggle">
            <span class="toggle-opt active" data-period="monthly">{html.escape(toggle_monthly)}</span>
            <span class="toggle-opt" data-period="annual">{html.escape(toggle_annual)} <span class="toggle-save">{html.escape(toggle_save)}</span></span>
        </div>
    </div>"""

    delay_classes = ["", " d1", " d2"]
    cards_parts = []

    for i, tier in enumerate(tiers):
        delay = delay_classes[i] if i < len(delay_classes) else ""
        tier_id = tier.get("id", "")
        name = tier.get("name", "")
        tagline = tier.get("tagline", "")
        price_monthly = tier.get("price_monthly", 0)
        price_annual = tier.get("price_annual", 0)
        cta_label = tier.get("cta_label", "")
        cta_href = tier.get("cta_href", "#start")
        cta_style = tier.get("cta_style", "ghost")
        featured = tier.get("featured", False)
        annual_note = tier.get("annual_note", "")
        features = tier.get("features", [])

        featured_class = " featured" if featured else ""

        # Badge for featured
        badge_html = ""
        if featured:
            badge_html = f'            <p class="price-badge">\n                {SVG_PRICE_BADGE_DOT}\n                Paling Populer\n            </p>\n'

        # Price period (only for non-free)
        period_html = ""
        if price_monthly > 0:
            period_html = '\n                <span class="price-period">rb / bln</span>'

        # Billed line id
        billed_id = ""
        if tier_id == "pro":
            billed_id = ' id="pro-billed"'
        elif tier_id == "biz":
            billed_id = ' id="biz-billed"'

        # CTA class
        cta_class = f"price-cta price-cta-{cta_style}"

        # Features HTML
        feat_parts = []
        for feat in features:
            text = feat.get("text", "")
            included = feat.get("included", True)
            svg = SVG_CHECK if included else SVG_CROSS
            dim_class = "" if included else " dim"
            feat_parts.append(
                f'                <li class="price-feat{dim_class}">\n'
                f'                    {svg}\n'
                f'                    {html.escape(text).replace("&amp;", "&amp;")}\n'
                f'                </li>'
            )

        feats_html = "\n".join(feat_parts)

        card = f"""        <div class="price-card{featured_class} reveal{delay}">
{badge_html}            <p class="price-tier">{html.escape(name)}</p>
            <p class="price-tagline">{html.escape(tagline)}</p>
            <div class="price-amount-wrap">
                <span class="price-currency">Rp</span>
                <span class="price-amount" data-monthly="{price_monthly}" data-annual="{price_annual}">{price_monthly}{period_html}</span>
            </div>
            <p class="price-billed"{billed_id}>&nbsp;</p>
            <a href="{html.escape(cta_href)}" class="{cta_class}">{html.escape(cta_label)}</a>
            <hr class="price-divider">
            <ul class="price-features">
{feats_html}
            </ul>
        </div>"""
        cards_parts.append(card)

    grid_html = f"""    <div class="pricing-grid">

{chr(10).join(cards_parts)}

    </div>"""

    return header_html + "\n\n" + grid_html


def render_faq(faq: dict) -> str:
    label = faq.get("section_label", "")
    heading_raw = faq.get("heading", "")
    heading_html = heading_raw.replace("\n", "<br>")
    contact_text = faq.get("contact_text", "")
    contact_link = faq.get("contact_link", "")
    contact_href = faq.get("contact_href", "#")
    items = faq.get("items", [])

    sticky_html = f"""        <div class="faq-sticky reveal">
            <p class="sec-label">{html.escape(label)}</p>
            <h2 class="sec-heading">{heading_html}</h2>
            <p class="sec-sub" style="margin-top:16px">{html.escape(contact_text)} <a href="{html.escape(contact_href)}" style="color:var(--accent);text-decoration:none;border-bottom:1px solid rgba(240,165,0,0.3)">{html.escape(contact_link)}</a></p>
        </div>"""

    item_parts = []
    for item in items:
        q = item.get("question", "")
        a = item.get("answer", "")
        item_html = f"""            <div class="faq-item">
                <button class="faq-q">
                    {html.escape(q)}
                    <span class="faq-icon" aria-hidden="true">
                        {SVG_FAQ_ICON}
                    </span>
                </button>
                <div class="faq-a">
                    <div class="faq-a-inner">{html.escape(a)}</div>
                </div>
            </div>"""
        item_parts.append(item_html)

    list_html = f"""        <div class="faq-list reveal d1">

{chr(10).join(item_parts)}

        </div>"""

    return sticky_html + "\n\n" + list_html


def render_cta_content(site: dict) -> str:
    cta = site.get("cta", {})
    label = cta.get("label", "")
    h1 = cta.get("heading_line1", "")
    h2 = cta.get("heading_line2", "")
    sub = cta.get("sub", "")
    cta_primary = cta.get("cta_primary", "")
    cta_primary_href = cta.get("cta_primary_href", "#")
    cta_secondary = cta.get("cta_secondary", "")
    cta_secondary_href = cta.get("cta_secondary_href", "#features")
    note = cta.get("note", "")

    return f"""    <p class="sec-label reveal">{html.escape(label)}</p>
    <h2 class="sec-heading reveal d1">{html.escape(h1)}<br>{html.escape(h2)}</h2>
    <p class="sec-sub reveal d2">{html.escape(sub).replace('—', '&mdash;')}</p>

    <div class="cta-actions reveal d3">
        <a href="{html.escape(cta_primary_href)}" class="btn-primary">
            {html.escape(cta_primary)}
            {SVG_HERO_ARROW}
        </a>
        <a href="{html.escape(cta_secondary_href)}" class="btn-ghost">{html.escape(cta_secondary)}</a>
    </div>

    <p class="cta-note reveal d4">{html.escape(note).replace('—', '&mdash;')}</p>"""


def render_footer_content(site: dict) -> str:
    footer = site.get("footer", {})
    links = footer.get("links", [])
    copyright_text = footer.get("copyright", "")
    status = footer.get("status", "")
    status_href = footer.get("status_href", "#")

    # Encode copyright symbol and em-dash
    copyright_html = copyright_text.replace("©", "&copy;").replace("—", "&mdash;")

    link_items = []
    for link in links:
        link_items.append(f'            <li><a href="{html.escape(link["href"])}">{html.escape(link["label"])}</a></li>')

    links_html = "\n".join(link_items)

    return f"""    <div class="footer-top">
        <div class="footer-logo">BASE.</div>
        <ul class="footer-links">
{links_html}
        </ul>
    </div>
    <div class="footer-bottom">
        <div class="footer-copy">{copyright_html}</div>
        <a href="{html.escape(status_href)}" class="footer-status">
            <span class="status-dot"></span>
            {html.escape(status)}
        </a>
    </div>"""


# ──────────────────────────────────────────────────────────────────────────────
# Main
# ──────────────────────────────────────────────────────────────────────────────
def main():
    print("Building website/index.html...")

    # Load template
    print("  Loading template...")
    template = TEMPLATE.read_text(encoding="utf-8")

    # Load YAML data
    print("  Loading YAML data...")
    def load_yaml(name):
        path = DATA_DIR / name
        with open(path, encoding="utf-8") as f:
            return yaml.safe_load(f)

    site         = load_yaml("site.yaml")
    features     = load_yaml("features.yaml")
    steps        = load_yaml("steps.yaml")
    testimonials = load_yaml("testimonials.yaml")
    pricing      = load_yaml("pricing.yaml")
    faq          = load_yaml("faq.yaml")

    # Inject sections
    sections = [
        ("nav_links",     render_nav_links(site)),
        ("drawer_nav",    render_drawer_nav(site)),
        ("hero",          render_hero(site)),
        ("features",      render_features(features)),
        ("steps",         render_steps(steps)),
        ("testimonials",  render_testimonials(testimonials)),
        ("pricing",       render_pricing(pricing)),
        ("faq",           render_faq(faq)),
        ("cta_content",   render_cta_content(site)),
        ("footer_content", render_footer_content(site)),
    ]

    result = template
    for key, content in sections:
        print(f"  Injecting {key}...")
        result = inject(result, key, content)

    # Write output
    OUTPUT.write_text(result, encoding="utf-8")
    lines = result.count("\n")
    print(f"Done -> website/index.html ({lines} lines)")


if __name__ == "__main__":
    main()
