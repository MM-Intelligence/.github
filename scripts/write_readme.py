"""Write profile/README.md. Badge URLs with embedded logos are long, so the
README is generated from the lists below. Run from the repo root:

  python scripts/write_readme.py --site <path to mm-intelligence>

The blog list between the BLOG-POST-LIST markers is refreshed daily by
.github/workflows/blog-posts.yml; the posts here only seed it.
"""

import argparse
import base64
import re
import urllib.parse
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

LINKEDIN_SVG = (
    '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="white"><path d="M20.45 20.45h-3.56'
    "v-5.57c0-1.33-.02-3.04-1.85-3.04-1.86 0-2.14 1.45-2.14 2.95v5.66H9.35V9h3.41v1.56h.05c.48-.9 1.64-1.85 "
    "3.37-1.85 3.6 0 4.27 2.37 4.27 5.46v6.28zM5.34 7.43a2.06 2.06 0 1 1 0-4.13 2.06 2.06 0 0 1 0 4.13zM7.12 "
    "20.45H3.56V9h3.56v11.45zM22.22 0H1.77C.79 0 0 .77 0 1.73v20.54C0 23.23.79 24 1.77 24h20.45c.98 0 "
    '1.78-.77 1.78-1.73V1.73C24 .77 23.2 0 22.22 0z"/></svg>'
)


def data_logo(svg: str) -> str:
    svg = svg.replace('fill="currentColor"', 'fill="white"')
    return "data:image/svg+xml;base64," + base64.b64encode(svg.encode()).decode()


def badge(label: str, color: str, logo: str, style: str = "for-the-badge", logo_color: str = "white") -> str:
    query = urllib.parse.urlencode({"style": style, "logo": logo, "logoColor": logo_color})
    text = label.replace("-", "--").replace("_", "__").replace(" ", "_")
    return f"https://img.shields.io/badge/{urllib.parse.quote(text)}-{color}?{query}"


def tech(name: str, logo: str) -> str:
    return f'<img src="{badge(name, "1A1625", logo, style="flat-square")}" alt="{name}"/>'


def build(site: Path) -> str:
    openai = data_logo((site / "public" / "logos" / "lobe-openai.svg").read_text(encoding="utf-8"))
    linkedin = data_logo(LINKEDIN_SVG)

    social = [
        ("mmintelligence.ai", "5227FF", "googlechrome", "white", "https://www.mmintelligence.ai"),
        ("Book a call", "FF9FFC", "googlecalendar", "0F0F0F", "https://www.mmintelligence.ai/contact"),
        ("LinkedIn", "0A66C2", linkedin, "white", "https://www.linkedin.com/company/mm-intelligence/"),
        ("YouTube", "FF0000", "youtube", "white", "https://www.youtube.com/@mm-intelligence"),
        ("Facebook", "1877F2", "facebook", "white", "https://www.facebook.com/people/MM-Intelligence/61576395188994/"),
        ("Email us", "0F0F0F", "gmail", "white", "mailto:info@mmintelligence.ai"),
    ]
    social_html = "\n".join(
        f'  <a href="{href}"><img src="{badge(label, color, logo, logo_color=lc)}" alt="{label}"/></a>'
        for label, color, logo, lc, href in social
    )

    partners = [
        ("nvidia-inception.svg", "NVIDIA Inception Program member", "https://www.nvidia.com/en-us/startups/"),
        ("openai-select-partner.svg", "OpenAI Select Partner",
         "https://www.mmintelligence.ai/blog/mm-intelligence-openai-select-partner"),
        ("elevenlabs.svg", "ElevenLabs Partner", "https://elevenlabs.io"),
        ("deepgram.svg", "Deepgram Startup Program", "https://deepgram.com/startups"),
    ]
    partner_html = "\n".join(
        f'  <a href="{url}"><img src="assets/partners/{file}" alt="{alt}" height="64"/></a>&nbsp;'
        for file, alt, url in partners
    )

    products = [
        ("mango", "Mango", "https://www.mangoanswers.com",
         "AI front desk that answers every call, books appointments and takes messages."),
        ("askmgm", "AskMGM", "https://askmgm.com",
         "Ask a question about Montgomery and get an answer from the city's own public data."),
        ("whatsgoodmgm", "WhatsGoodMGM", "https://whatsgoodmgm.com",
         "A weekly curated guide to what's happening in Montgomery."),
        ("matemove", "MateMove", "https://apps.apple.com/us/app/matemove/id6753686255",
         "Free, private, all-in-one fitness tracker for iPhone."),
    ]

    def product_cell(slug: str, name: str, url: str, blurb: str) -> str:
        return (
            f'<td width="50%" valign="top">\n'
            f'<a href="{url}"><img src="assets/products/{slug}.png" alt="{name}" width="100%"/></a>\n'
            f'<h3><a href="{url}">{name}</a></h3>\n{blurb}\n</td>'
        )

    product_rows = "\n".join(
        "<tr>\n" + "\n".join(product_cell(*p) for p in products[i:i + 2]) + "\n</tr>" for i in (0, 2)
    )

    services = [
        ("Voice agents", "Answer the phone, book appointments and take messages, in English and Arabic.",
         "https://www.mmintelligence.ai/services/voice"),
        ("AI systems", "Answer from your own documents, on your site or on WhatsApp.",
         "https://www.mmintelligence.ai/services/chatbots"),
        ("Automations", "Take the repetitive work off your team's plate.",
         "https://www.mmintelligence.ai/services/automation"),
        ("Web and mobile apps", "Built and shipped in weeks, not months.",
         "https://www.mmintelligence.ai/services/development"),
    ]
    service_cells = "\n".join(
        f'<td width="25%" valign="top"><a href="{url}"><b>{title}</b></a><br/><sub>{text}</sub></td>'
        for title, text, url in services
    )

    stack = [
        ("AI and LLMs", [("Anthropic", "anthropic"), ("OpenAI", openai), ("Gemini", "googlegemini"),
                         ("LangChain", "langchain"), ("LangGraph", "langgraph"),
                         ("Hugging Face", "huggingface"), ("Ollama", "ollama")]),
        ("Voice", [("ElevenLabs", "elevenlabs"), ("Deepgram", "deepgram"), ("LiveKit", "livekit")]),
        ("Data and ML", [("PyTorch", "pytorch"), ("scikit-learn", "scikitlearn"), ("pandas", "pandas"),
                         ("NumPy", "numpy"), ("Jupyter", "jupyter"), ("Apache Spark", "apachespark"),
                         ("Airflow", "apacheairflow"), ("Snowflake", "snowflake")]),
        ("Languages", [("Python", "python"), ("TypeScript", "typescript"), ("Swift", "swift"), ("Go", "go")]),
        ("Apps and infra", [("Next.js", "nextdotjs"), ("React", "react"), ("FastAPI", "fastapi"),
                            ("Node.js", "nodedotjs"), ("PostgreSQL", "postgresql"), ("Supabase", "supabase"),
                            ("Redis", "redis"), ("Docker", "docker"), ("Google Cloud", "googlecloud"),
                            ("Vercel", "vercel"), ("Cloudflare", "cloudflare"), ("n8n", "n8n")]),
    ]
    stack_rows = "\n".join(
        f'<tr><td><b>{group}</b></td><td>\n{" ".join(tech(n, logo) for n, logo in items)}\n</td></tr>'
        for group, items in stack
    )

    posts = [
        ("Teaching Seniors to Use ChatGPT on a Phone: What Worked in Montgomery",
         "teaching-seniors-chatgpt-phone-montgomery"),
        ("The Five Automations That Pay Back Fastest for River Region Small Businesses",
         "five-automations-river-region-small-business"),
        ("Miss Odessa: Building a Voice AI Guide to Montgomery's History Buses",
         "miss-odessa-voice-ai-montgomery-history"),
        ("MM Intelligence Named an OpenAI Select Partner", "mm-intelligence-openai-select-partner"),
        ("Building a Beacon Tour for a Historic District (Without Drilling a Single Hole)",
         "beacon-tour-historic-district-build"),
    ]
    post_list = "\n".join(f"- [{t}](https://www.mmintelligence.ai/blog/{s})" for t, s in posts)

    return f"""<div align="center">

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="assets/banner-dark.svg">
  <img src="assets/banner-light.svg" alt="MM Intelligence: AI-native software, built to work." width="100%">
</picture>

<p>
{social_html}
</p>

<p>
{partner_html}
</p>

</div>

We're an AI-native software company in **Montgomery, Alabama**, with a registered office in **Manama, Bahrain**. We build voice agents, AI systems, automations, and web and mobile apps for businesses in the US and the Gulf, and we run products of our own.

## Products we run

<table>
{product_rows}
</table>

## What we build

<table>
<tr>
{service_cells}
</tr>
</table>

## Our stack

<table>
{stack_rows}
</table>

## Latest from the blog

<!-- BLOG-POST-LIST:START -->
{post_list}
<!-- BLOG-POST-LIST:END -->

<sub>Updated daily from [our blog](https://www.mmintelligence.ai/blog).</sub>

---

<div align="center">

**Montgomery, Alabama** &nbsp;·&nbsp; **Manama, Bahrain**<br/>
[info@mmintelligence.ai](mailto:info@mmintelligence.ai) &nbsp;·&nbsp; [Book a call](https://www.mmintelligence.ai/contact) &nbsp;·&nbsp; [mmintelligence.ai](https://www.mmintelligence.ai)

</div>
"""


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--site", type=Path, required=True)
    args = parser.parse_args()
    (ROOT / "profile" / "README.md").write_text(build(args.site), encoding="utf-8")


if __name__ == "__main__":
    main()
