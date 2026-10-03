import json
from bisect import bisect_right
from pathlib import Path
from typing import Dict, NamedTuple, Optional, Tuple

ICONS_FILE = Path(__file__).resolve().parent / "assets" / "icons.json"
DEFAULT_CLASS = "_"


class EntityIcons(NamedTuple):
    default: Optional[str]
    states: Dict[str, str]
    range_bounds: Tuple[float, ...]
    range_glyphs: Tuple[str, ...]


def _load():
    data = json.loads(ICONS_FILE.read_text(encoding="utf-8"))
    codepoints = data["icons"]

    def glyph(name):
        return chr(int(codepoints[name], 16)) if name in codepoints else None

    def entity_icons(variant: dict) -> EntityIcons:
        ranges = sorted((float(bound), glyph(name)) for bound, name in variant.get("range", {}).items())
        return EntityIcons(
            glyph(variant.get("default")),
            {state: glyph(name) for state, name in variant.get("state", {}).items()},
            tuple(bound for bound, _ in ranges),
            tuple(glyph for _, glyph in ranges),
        )

    domains = {
        domain: {device_class: entity_icons(variant) for device_class, variant in variants.items()}
        for domain, variants in data["domains"].items()
    }
    return codepoints, domains


CODEPOINTS, DOMAINS = _load()


def icon(name: Optional[str]) -> Optional[str]:
    """Glyph for an MDI icon name, with or without the ``mdi:`` prefix."""
    if not name:
        return None
    codepoint = CODEPOINTS.get(name[4:] if name.startswith("mdi:") else name)
    return chr(int(codepoint, 16)) if codepoint else None


def _range_glyph(icons: EntityIcons, state: Optional[str]) -> Optional[str]:
    if not icons.range_bounds or state is None:
        return None
    try:
        index = bisect_right(icons.range_bounds, float(state)) - 1
    except ValueError:
        return None
    return icons.range_glyphs[max(index, 0)]


def entity_icon(domain: str, state: Optional[str] = None, device_class: Optional[str] = None) -> Optional[str]:
    """Glyph Home Assistant shows for an entity of this domain, state and device class."""
    variants = DOMAINS.get(domain)
    if not variants:
        return None
    default = variants.get(DEFAULT_CLASS)
    for icons in (variants.get(device_class), default):
        if icons is None:
            continue
        glyph = icons.states.get(state) or _range_glyph(icons, state) or icons.default
        if glyph:
            return glyph
    return None
