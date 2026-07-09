"""Generate professional placeholder assets for BehaviorGraph README."""

from __future__ import annotations

from pathlib import Path

try:
    from PIL import Image, ImageDraw, ImageFont
except ImportError as exc:  # pragma: no cover
    raise SystemExit("Pillow is required: pip install pillow") from exc

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "assets"
SHOTS = ASSETS / "screenshots"
ASSETS.mkdir(parents=True, exist_ok=True)
SHOTS.mkdir(parents=True, exist_ok=True)

BG = (11, 18, 32)
PANEL = (18, 26, 43)
ACCENT = (94, 234, 212)
ACCENT2 = (56, 189, 248)
TEXT = (232, 238, 252)
MUTED = (157, 176, 208)
LINE = (36, 48, 73)


def font(size: int):
    for name in (
        "C:/Windows/Fonts/segoeuib.ttf",
        "C:/Windows/Fonts/segoeui.ttf",
        "arial.ttf",
    ):
        try:
            return ImageFont.truetype(name, size)
        except OSError:
            continue
    return ImageFont.load_default()


def draw_panel(draw: ImageDraw.ImageDraw, xy, title: str, body: str):
    x0, y0, x1, y1 = xy
    draw.rounded_rectangle(xy, radius=18, fill=PANEL, outline=LINE, width=2)
    draw.text((x0 + 22, y0 + 18), title, fill=ACCENT, font=font(22))
    draw.text((x0 + 22, y0 + 56), body, fill=MUTED, font=font(16))


def make_icon():
    img = Image.new("RGB", (512, 512), BG)
    d = ImageDraw.Draw(img)
    d.ellipse((56, 56, 456, 456), outline=ACCENT, width=18)
    # graph nodes
    nodes = [(160, 180), (350, 160), (250, 300), (360, 340), (150, 340)]
    for i, (x, y) in enumerate(nodes):
        d.ellipse((x - 18, y - 18, x + 18, y + 18), fill=ACCENT2 if i % 2 else ACCENT)
    d.line((160, 180, 350, 160), fill=TEXT, width=6)
    d.line((160, 180, 250, 300), fill=TEXT, width=6)
    d.line((350, 160, 360, 340), fill=TEXT, width=6)
    d.line((250, 300, 150, 340), fill=TEXT, width=6)
    d.line((250, 300, 360, 340), fill=TEXT, width=6)
    d.text((168, 400), "BG", fill=TEXT, font=font(64))
    img.save(ASSETS / "icon.png")


def make_hero():
    img = Image.new("RGB", (1600, 900), BG)
    d = ImageDraw.Draw(img)
    d.text((72, 70), "BEHAVIORGRAPH", fill=ACCENT, font=font(28))
    d.text((72, 130), "Events → Journeys → Activation → Retention", fill=TEXT, font=font(42))
    d.text(
        (72, 210),
        "Behavioral analytics studio for product paths, friction and opportunity memos.",
        fill=MUTED,
        font=font(24),
    )
    draw_panel(d, (72, 320, 520, 560), "Activation", "Funnel drop radar\nUnique-user conversion")
    draw_panel(d, (560, 320, 1020, 560), "Journey graph", "NetworkX path map\nSession transitions")
    draw_panel(d, (1080, 320, 1528, 560), "Opportunity memo", "Friction → hypothesis\nExplicit limitations")
    draw_panel(
        d,
        (72, 600, 1528, 820),
        "MVP scope",
        "Synthetic events · taxonomy · cohorts · segments · no production tracking",
    )
    img.save(ASSETS / "hero-cover.png")


def make_social():
    img = Image.new("RGB", (1280, 640), BG)
    d = ImageDraw.Draw(img)
    d.text((64, 180), "BehaviorGraph", fill=ACCENT, font=font(64))
    d.text(
        (64, 280),
        "Which paths lead to activation, churn or habit?",
        fill=TEXT,
        font=font(32),
    )
    d.text(
        (64, 360),
        "Funnels · Cohorts · Journey Graph · Friction Radar",
        fill=MUTED,
        font=font(26),
    )
    img.save(ASSETS / "social-preview.png")


def make_architecture():
    img = Image.new("RGB", (1600, 700), BG)
    d = ImageDraw.Draw(img)
    steps = [
        (40, "Events"),
        (260, "Taxonomy"),
        (480, "Funnel"),
        (700, "Cohorts"),
        (920, "Graph"),
        (1140, "Friction"),
        (1360, "Memo"),
    ]
    d.text((40, 40), "BehaviorGraph analytical journey", fill=TEXT, font=font(36))
    for i, (x, label) in enumerate(steps):
        d.rounded_rectangle((x, 220, x + 180, 360), radius=16, fill=PANEL, outline=ACCENT, width=2)
        d.text((x + 28, 270), label, fill=TEXT, font=font(22))
        if i < len(steps) - 1:
            d.line((x + 180, 290, steps[i + 1][0], 290), fill=LINE, width=4)
    d.text(
        (40, 460),
        "Next.js UI  ·  FastAPI analytics  ·  Pandas/NetworkX/DuckDB  ·  Synthetic seed events",
        fill=MUTED,
        font=font(22),
    )
    img.save(ASSETS / "architecture-pipeline.png")


def make_shots():
    specs = [
        ("01-hero-behavior-cockpit.png", "Behavior Cockpit", "Users, events, sessions and activation rate"),
        ("02-event-taxonomy-center.png", "Event Taxonomy Center", "Owned event contract for product analytics"),
        ("03-activation-funnel.png", "Activation Funnel", "Unique-user conversion across onboarding steps"),
        ("04-retention-cohorts.png", "Retention Cohorts", "Week-based retention matrix for demo cohorts"),
        ("05-journey-path-graph.png", "Journey Path Graph", "NetworkX session transitions as a path map"),
        ("06-feature-adoption-board.png", "Feature Adoption Board", "Which features stick after activation"),
        ("07-friction-radar.png", "Friction Radar", "Drop severity and error-like event signals"),
        ("08-opportunity-memo.png", "Product Opportunity Memo", "Hypotheses with explicit analytical limits"),
    ]
    for name, title, subtitle in specs:
        img = Image.new("RGB", (1400, 860), BG)
        d = ImageDraw.Draw(img)
        d.rounded_rectangle((40, 40, 1360, 820), radius=24, fill=PANEL, outline=LINE, width=2)
        d.text((80, 90), "BehaviorGraph", fill=ACCENT, font=font(24))
        d.text((80, 150), title, fill=TEXT, font=font(48))
        d.text((80, 230), subtitle, fill=MUTED, font=font(26))
        d.rounded_rectangle((80, 320, 1320, 720), radius=18, fill=(14, 22, 36), outline=LINE, width=2)
        d.text(
            (110, 360),
            "Preview placeholder — replace with product screenshots after UI polish.",
            fill=MUTED,
            font=font(22),
        )
        d.text(
            (110, 430),
            "Events → Taxonomy → Funnel → Cohorts → Graph → Friction → Memo",
            fill=TEXT,
            font=font(24),
        )
        img.save(SHOTS / name)


if __name__ == "__main__":
    make_icon()
    make_hero()
    make_social()
    make_architecture()
    make_shots()
    print(f"Assets written to {ASSETS}")
