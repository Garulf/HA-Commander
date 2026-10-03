"""Download the Material Design Icons font and build src/plugin/assets/icons.json.

Usage: python scripts/update_icons.py   (bump the pinned versions below first)

icons.json holds every MDI icon name and alias mapped to its codepoint, plus the
entity icons Home Assistant uses for each domain: a default, per-state icons,
battery-style numeric ranges and per-device_class variants.
"""
import json
import re
import sys
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

MDI_VERSION = "7.4.47"
HA_VERSION = "2026.9.4"

ASSETS_DIR = Path(__file__).resolve().parents[1] / "src" / "plugin" / "assets"
FONT_URL = f"https://cdn.jsdelivr.net/npm/@mdi/font@{MDI_VERSION}/fonts/materialdesignicons-webfont.ttf"
META_URL = f"https://cdn.jsdelivr.net/npm/@mdi/svg@{MDI_VERSION}/meta.json"
CORE_URL = f"https://raw.githubusercontent.com/home-assistant/core/{HA_VERSION}/homeassistant"
FRONTEND_URL = "https://raw.githubusercontent.com/home-assistant/frontend/{version}/src/data/icons.ts"
HELPER_DOMAINS = [
    "automation", "counter", "group", "input_boolean", "input_button", "input_datetime",
    "input_number", "input_select", "input_text", "person", "schedule", "scene", "script",
    "sun", "timer", "zone",
]


def fetch(url: str) -> bytes:
    with urllib.request.urlopen(url, timeout=30) as response:
        return response.read()


def mdi_name(icon: str) -> str:
    return icon.split(":", 1)[1] if icon.startswith("mdi:") else icon


def camel_to_kebab(name: str) -> str:
    return re.sub(r"(?<=[a-z0-9])(?=[A-Z0-9])", "-", name).lower()


def mdi_codepoints() -> dict:
    meta = json.loads(fetch(META_URL))
    codepoints = {alias: icon["codepoint"] for icon in meta for alias in icon["aliases"]}
    codepoints.update({icon["name"]: icon["codepoint"] for icon in meta})
    return codepoints


def entity_domains() -> list:
    source = fetch(f"{CORE_URL}/generated/entity_platforms.py").decode()
    platforms = re.findall(r'^\s+\w+ = "(\w+)"$', source, re.MULTILINE)
    return sorted(set(platforms) | set(HELPER_DOMAINS))


def frontend_fallbacks() -> dict:
    manifest = json.loads(fetch(f"{CORE_URL}/components/frontend/manifest.json"))
    version = manifest["requirements"][0].split("==")[1]
    source = fetch(FRONTEND_URL.format(version=version)).decode()
    block = re.search(r"FALLBACK_DOMAIN_ICONS = \{(.*?)\n\};", source, re.DOTALL).group(1)
    return {domain: camel_to_kebab(icon[3:]) for domain, icon in re.findall(r"(\w+): (mdi\w+)", block)}


def domain_icons(domain: str):
    try:
        icons = json.loads(fetch(f"{CORE_URL}/components/{domain}/icons.json"))
    except urllib.error.HTTPError:
        return domain, {}
    return domain, icons.get("entity_component") or {}


def clean(variant: dict) -> dict:
    cleaned = {}
    if "default" in variant:
        cleaned["default"] = mdi_name(variant["default"])
    for key in ("state", "range"):
        if variant.get(key):
            cleaned[key] = {value: mdi_name(icon) for value, icon in variant[key].items()}
    return cleaned


def main() -> int:
    (ASSETS_DIR / "materialdesignicons-webfont.ttf").write_bytes(fetch(FONT_URL))
    codepoints = mdi_codepoints()
    fallbacks = frontend_fallbacks()

    with ThreadPoolExecutor(max_workers=16) as pool:
        components = dict(pool.map(domain_icons, sorted(set(entity_domains()) | set(fallbacks))))

    domains = {}
    for domain, variants in sorted(components.items()):
        cleaned = {device_class: clean(variant) for device_class, variant in variants.items()}
        cleaned = {device_class: variant for device_class, variant in cleaned.items() if variant}
        if domain in fallbacks:
            cleaned.setdefault("_", {}).setdefault("default", fallbacks[domain])
        if cleaned:
            domains[domain] = cleaned

    used = {
        icon
        for variants in domains.values()
        for variant in variants.values()
        for icon in [variant.get("default"), *variant.get("state", {}).values(), *variant.get("range", {}).values()]
        if icon
    }
    missing = sorted(used - codepoints.keys())
    if missing:
        print(f"Icons missing from MDI {MDI_VERSION}: {', '.join(missing)}", file=sys.stderr)

    data = {"mdi_version": MDI_VERSION, "ha_version": HA_VERSION, "icons": codepoints, "domains": domains}
    (ASSETS_DIR / "icons.json").write_text(json.dumps(data, separators=(",", ":"), sort_keys=True) + "\n", encoding="utf-8")
    print(f"Wrote {len(codepoints)} icon names and {len(domains)} domains")
    return 0


if __name__ == "__main__":
    sys.exit(main())
