"""Build the images for the MM Intelligence GitHub org profile.

Writes assets/ next to profile/README.md:
  banner-dark.svg, banner-light.svg   animated header (fonts embedded)
  products/<slug>.png                 product cards with a browser frame
  partners/<slug>.svg                 partner badges

Run from the repo root:
  python scripts/build_assets.py --fonts <dir> --site <path to mm-intelligence>

<dir> holds Outfit.ttf, InstrumentSerif-Italic.ttf and SpaceMono-Regular.ttf
from github.com/google/fonts. Needs Pillow and fontTools.
"""

import argparse
import base64
import io
import shutil
from pathlib import Path

from fontTools import subset
from fontTools.ttLib import TTFont
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent.parent
ASSETS = ROOT / "profile" / "assets"

PURPLE = "#5227FF"
PINK = "#FF9FFC"
LAVENDER = "#B19EEF"

TAGLINES = [
    "voice agents that answer every call",
    "AI that answers from your own documents",
    "automations that take the busywork",
    "web and mobile apps, shipped in weeks",
]

PRODUCTS = [
    ("mango", "mango.png", "mangoanswers.com"),
    ("askmgm", "askmgm.png", "askmgm.com"),
    ("whatsgoodmgm", "WhatsGoodMGM.png", "whatsgoodmgm.com"),
    ("matemove", "MateMove.png", "apps.apple.com/matemove"),
]


def font_face(path: Path, family: str, text: str, style: str = "normal", weight: str = "400",
              variation: dict | None = None) -> str:
    """Subset a font to the characters in `text` and return a base64 @font-face rule."""
    font = TTFont(path)
    if variation:
        from fontTools.varLib import instancer
        font = instancer.instantiateVariableFont(font, variation)
    options = subset.Options()
    options.layout_features = ["*"]
    subsetter = subset.Subsetter(options)
    subsetter.populate(text=text)
    subsetter.subset(font)
    buf = io.BytesIO()
    font.save(buf)
    data = base64.b64encode(buf.getvalue()).decode()
    return (f"@font-face{{font-family:'{family}';font-style:{style};font-weight:{weight};"
            f"src:url(data:font/ttf;base64,{data}) format('truetype');}}")


def logo_data_uri(site: Path, dark_text: bool) -> tuple[str, int, int]:
    """The MIM mark, resized. On a light banner the white middle bar turns near-black."""
    im = Image.open(site / "public" / "images" / "logo.png").convert("RGBA")
    im.thumbnail((360, 140), Image.LANCZOS)
    if dark_text:
        px = im.load()
        for y in range(im.height):
            for x in range(im.width):
                r, g, b, a = px[x, y]
                if a and r > 200 and g > 200 and b > 200:
                    px[x, y] = (15, 15, 15, a)
    buf = io.BytesIO()
    im.save(buf, "PNG", optimize=True)
    return "data:image/png;base64," + base64.b64encode(buf.getvalue()).decode(), im.width, im.height


def banner(fonts: Path, site: Path, dark: bool) -> str:
    w, h = 1280, 400
    bg = "#0F0F0F" if dark else "#FFFFFF"
    fg = "#FAFAFA" if dark else "#0F0F0F"
    muted = "#8A8A93" if dark else "#5B5B66"
    grid = "rgba(82,39,255,0.07)" if dark else "rgba(82,39,255,0.06)"
    glow = 0.55 if dark else 0.28

    headline = "AI-native software,"
    accent = "built to work."
    label = "// AI-NATIVE SOFTWARE COMPANY"
    footer = "MONTGOMERY, AL  ·  MANAMA, BH  ·  SERVING THE US AND THE GULF"
    prompt = "~/mmi $"
    mono_text = label + footer + prompt + "".join(TAGLINES) + "_"

    css_fonts = "".join([
        font_face(fonts / "Outfit.ttf", "Outfit", headline, weight="700", variation={"wght": 700}),
        font_face(fonts / "InstrumentSerif-Italic.ttf", "Instrument Serif", accent, style="italic"),
        font_face(fonts / "SpaceMono-Regular.ttf", "Space Mono", mono_text),
    ])

    logo, lw, lh = logo_data_uri(site, dark_text=not dark)
    logo_h = 54
    logo_w = round(lw * logo_h / lh)

    # One tagline is visible at a time: each fades in, holds, and fades out
    # inside its own quarter of the cycle.
    cycle = 3.2 * len(TAGLINES)
    tagline_css = "".join(
        f".t{i}{{animation:tag {cycle}s linear infinite;animation-delay:{i * 3.2}s;opacity:0}}"
        for i in range(len(TAGLINES))
    )
    share = 100 / len(TAGLINES)
    tag_keyframes = (
        f"@keyframes tag{{0%{{opacity:0;transform:translateY(8px)}}"
        f"{share * 0.12:.2f}%{{opacity:1;transform:translateY(0)}}"
        f"{share * 0.85:.2f}%{{opacity:1;transform:translateY(0)}}"
        f"{share:.2f}%{{opacity:0;transform:translateY(-8px)}}100%{{opacity:0}}}}"
    )

    taglines = "".join(
        f'<text class="mono t{i}" x="196" y="328" font-size="24" fill="{fg}">{t}</text>'
        for i, t in enumerate(TAGLINES)
    )

    # Voice waveform on the right: bars pulse at staggered delays.
    bars = []
    n = 28
    for i in range(n):
        x = 860 + i * 13
        delay = (i * 0.11) % 1.4
        bars.append(
            f'<rect class="bar" x="{x}" y="160" width="6" height="80" rx="3" '
            f'style="animation-delay:-{delay:.2f}s" fill="url(#wave)"/>'
        )

    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img" aria-label="MM Intelligence: AI-native software, built to work.">
<defs>
<style>{css_fonts}
.display{{font-family:'Outfit',system-ui,sans-serif;font-weight:700}}
.serif{{font-family:'Instrument Serif',Georgia,serif;font-style:italic}}
.mono{{font-family:'Space Mono',ui-monospace,monospace}}
.g1{{animation:drift1 14s ease-in-out infinite alternate}}
.g2{{animation:drift2 18s ease-in-out infinite alternate}}
@keyframes drift1{{from{{transform:translate(0,0)}}to{{transform:translate(160px,40px)}}}}
@keyframes drift2{{from{{transform:translate(0,0)}}to{{transform:translate(-180px,-30px)}}}}
.cursor{{animation:blink 1s steps(1) infinite}}
@keyframes blink{{50%{{opacity:0}}}}
.bar{{transform-box:fill-box;transform-origin:center;animation:pulse 1.4s ease-in-out infinite}}
@keyframes pulse{{0%,100%{{transform:scaleY(.18)}}50%{{transform:scaleY(1)}}}}
{tagline_css}{tag_keyframes}
</style>
<linearGradient id="accent" x1="0" x2="1" y1="0" y2="0">
<stop offset="0" stop-color="{PURPLE}"/><stop offset=".5" stop-color="{PINK}"/><stop offset="1" stop-color="{LAVENDER}"/>
</linearGradient>
<linearGradient id="wave" x1="0" x2="0" y1="0" y2="1">
<stop offset="0" stop-color="{PINK}"/><stop offset="1" stop-color="{PURPLE}"/>
</linearGradient>
<pattern id="grid" width="40" height="40" patternUnits="userSpaceOnUse">
<path d="M40 0H0V40" fill="none" stroke="{grid}" stroke-width="1"/>
</pattern>
<filter id="blur" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="70"/></filter>
<clipPath id="card"><rect width="{w}" height="{h}" rx="24"/></clipPath>
</defs>
<g clip-path="url(#card)">
<rect width="{w}" height="{h}" fill="{bg}"/>
<rect width="{w}" height="{h}" fill="url(#grid)"/>
<g filter="url(#blur)" opacity="{glow}">
<circle class="g1" cx="250" cy="90" r="150" fill="{PURPLE}"/>
<circle class="g2" cx="1050" cy="330" r="170" fill="{PINK}" opacity=".7"/>
</g>
<image href="{logo}" x="80" y="48" width="{logo_w}" height="{logo_h}"/>
<text class="mono" x="80" y="146" font-size="14" letter-spacing="3" fill="{muted}">{label}</text>
<text class="display" x="78" y="208" font-size="58" fill="{fg}">{headline}</text>
<text class="serif" x="80" y="272" font-size="60" fill="url(#accent)">{accent}</text>
<text class="mono" x="80" y="328" font-size="24" fill="{PURPLE}">{prompt}</text>
{taglines}
<text class="mono" x="80" y="372" font-size="13" letter-spacing="2.5" fill="{muted}">{footer}</text>
{''.join(bars)}
</g>
<rect x=".5" y=".5" width="{w - 1}" height="{h - 1}" rx="24" fill="none" stroke="{'#26262B' if dark else '#E4E4EA'}"/>
</svg>
"""


def rounded_mask(size: tuple[int, int], radius: int) -> Image.Image:
    mask = Image.new("L", size, 0)
    ImageDraw.Draw(mask).rounded_rectangle([0, 0, size[0] - 1, size[1] - 1], radius, fill=255)
    return mask


def product_card(fonts: Path, src: Path, domain: str, out: Path) -> None:
    """Screenshot in a dark browser frame with the product's address in the bar."""
    w, bar = 960, 46
    shot = Image.open(src).convert("RGB")
    content_h = 540
    # Cover the content area, keeping the top of the screenshot.
    scale = max(w / shot.width, content_h / shot.height)
    shot = shot.resize((round(shot.width * scale), round(shot.height * scale)), Image.LANCZOS)
    left = (shot.width - w) // 2
    shot = shot.crop((left, 0, left + w, content_h))

    card = Image.new("RGB", (w, bar + content_h), "#16141C")
    d = ImageDraw.Draw(card)
    for i, color in enumerate(["#FF5F57", "#FEBC2E", "#28C840"]):
        d.ellipse([18 + i * 20, 17, 30 + i * 20, 29], fill=color)
    mono = ImageFont.truetype(str(fonts / "SpaceMono-Regular.ttf"), 15)
    pill_w = 320
    px0 = (w - pill_w) // 2
    d.rounded_rectangle([px0, 10, px0 + pill_w, 36], 8, fill="#0F0F12")
    text_w = d.textlength(domain, font=mono)
    d.text(((w - text_w) / 2, 13), domain, font=mono, fill="#B9B6C8")
    card.paste(shot, (0, bar))

    rgba = card.convert("RGBA")
    rgba.putalpha(rounded_mask(rgba.size, 18))
    rgba.save(out, "PNG", optimize=True)


def partner_badge(name: str, line: str, icon_svg: str, icon_color: str) -> str:
    """Badge in the same shape as the OpenAI Select Partner badge (375x177, white, black border)."""
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="375" height="177" viewBox="0 0 375 177" role="img" aria-label="{name} {line}">
<rect x="1.5" y="1.5" width="372" height="174" rx="18.5" fill="#fff" stroke="#000" stroke-width="3"/>
<g transform="translate(46 50) scale(3.2)" fill="{icon_color}">{icon_svg}</g>
<text x="150" y="86" font-family="Segoe UI,Helvetica,Arial,sans-serif" font-size="30" font-weight="700" fill="#000">{name}</text>
<text x="150" y="122" font-family="Segoe UI,Helvetica,Arial,sans-serif" font-size="22" fill="#333">{line}</text>
</svg>
"""


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--fonts", type=Path, required=True)
    parser.add_argument("--site", type=Path, required=True)
    args = parser.parse_args()

    (ASSETS / "products").mkdir(parents=True, exist_ok=True)
    (ASSETS / "partners").mkdir(parents=True, exist_ok=True)

    (ASSETS / "banner-dark.svg").write_text(banner(args.fonts, args.site, dark=True), encoding="utf-8")
    (ASSETS / "banner-light.svg").write_text(banner(args.fonts, args.site, dark=False), encoding="utf-8")

    for slug, file, domain in PRODUCTS:
        product_card(args.fonts, args.site / "public" / "products" / file, domain,
                     ASSETS / "products" / f"{slug}.png")

    logos = args.site / "public" / "logos"
    # Crop the NVIDIA badge to its border so it matches the others in height.
    nvidia = (logos / "nvidia-inception.svg").read_text(encoding="utf-8")
    nvidia = nvidia.replace('viewBox="0 0 500.4288 216"', 'viewBox="25 25 450.5 166"', 1)
    (ASSETS / "partners" / "nvidia-inception.svg").write_text(nvidia, encoding="utf-8")
    shutil.copy(logos / "openai-select-partner.svg", ASSETS / "partners" / "openai-select-partner.svg")
    eleven = '<path d="M5 0h5v24H5V0zM14 0h5v24h-5V0z"/>'
    deepgram_svg = (logos / "deepgram.svg").read_text(encoding="utf-8")
    deepgram_path = deepgram_svg[deepgram_svg.index("<path"):deepgram_svg.rindex("</svg>")]
    (ASSETS / "partners" / "elevenlabs.svg").write_text(
        partner_badge("ElevenLabs", "Partner", eleven, "#000"), encoding="utf-8")
    (ASSETS / "partners" / "deepgram.svg").write_text(
        partner_badge("Deepgram", "Startup Program", deepgram_path, "#000"), encoding="utf-8")


if __name__ == "__main__":
    main()
