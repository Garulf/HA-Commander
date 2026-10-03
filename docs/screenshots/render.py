"""Render the README screenshots and hero image with flow-render.

Usage (from the repo root, with flow-render and Pillow installed):

    python docs/screenshots/render.py

Each ``<shot>.json`` is a flow-render config whose results name a Material
Design icon in ``glyph`` instead of an image ``icon``. Flow Launcher draws those
glyphs in the theme's text colour, so they are rasterized per theme first.
"""
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[2]
SHOTS_DIR = ROOT / "docs" / "screenshots"
ASSETS_DIR = ROOT / ".github" / "assets"
PLUGIN_ASSETS = ROOT / "src" / "plugin" / "assets"
THEMES = {"dark": "#FFFFFF", "light": "#1B1B1B"}
HERO = {"shot": "hero", "theme": "dark", "css": ["win11-dark.css", "docs/screenshots/hero.css"]}

CODEPOINTS = json.loads((PLUGIN_ASSETS / "icons.json").read_text(encoding="utf-8"))["icons"]
FONT = ImageFont.truetype(str(PLUGIN_ASSETS / "materialdesignicons-webfont.ttf"), 112)


def glyph_png(name: str, color: str, out_dir: Path) -> Path:
    path = out_dir / f"{name}-{color.lstrip('#')}.png"
    if not path.exists():
        image = Image.new("RGBA", (128, 128), (0, 0, 0, 0))
        ImageDraw.Draw(image).text((64, 64), chr(int(CODEPOINTS[name], 16)), font=FONT, fill=color, anchor="mm")
        image.save(path)
    return path


def flow_render(args, out_path: Path) -> None:
    with tempfile.TemporaryDirectory() as out_dir:
        subprocess.run(["flow-render", *args, "-o", out_dir], check=True, cwd=ROOT)
        (rendered,) = Path(out_dir).glob("*.png")
        shutil.move(str(rendered), out_path)
    print(f"Wrote {out_path}")


def render_config(shot: str, theme: str, css: str, out_path: Path, work: Path) -> None:
    config = json.loads((SHOTS_DIR / f"{shot}.json").read_text(encoding="utf-8"))
    config["icon"] = str((SHOTS_DIR / config["icon"]).resolve())
    for result in config["results"]:
        result["icon"] = str(glyph_png(result.pop("glyph"), THEMES[theme], work))
    config["css"] = css
    config_path = work / f"{shot}-{theme}.json"
    config_path.write_text(json.dumps(config), encoding="utf-8")
    flow_render(["-c", str(config_path)], out_path)


def main() -> None:
    shots = sorted(path.stem for path in SHOTS_DIR.glob("*.json") if path.stem != HERO["shot"])
    with tempfile.TemporaryDirectory() as tmp:
        work = Path(tmp)
        for shot in shots:
            for theme in THEMES:
                render_config(shot, theme, f"win11-{theme}.css", ASSETS_DIR / f"{shot}-{theme}.png", work)
        render_config(HERO["shot"], HERO["theme"], HERO["css"], ASSETS_DIR / "hero.png", work)

        package = subprocess.run([str(ROOT / "scripts" / "package.sh"), str(work / "dist")], check=True, capture_output=True, text=True)
        plugin_zip = package.stdout.strip().splitlines()[-1]
        for theme in THEMES:
            flow_render(["-u", plugin_zip, "-i", "-s", f"win11-{theme}", "--hide-caret"], ASSETS_DIR / f"install-{theme}.png")


if __name__ == "__main__":
    sys.exit(main())
