from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from pyflowlauncher import Result, api
from pyflowlauncher.models.result import Glyph, PreviewInfo

PLUGIN_DIR = Path(__file__).resolve().parent
ICON = str(PLUGIN_DIR.parent / "icon.png")
FONT = str(PLUGIN_DIR / "assets" / "MaterialDesignIconsDesktop.ttf")


@dataclass
class HassResult(Result):
    settings_change: Optional[dict] = None

    def to_json(self):
        result = super().to_json()
        # pyflowlauncher 1.2.1 sends "Preview": null, which crashes Flow
        # Launcher's preview panel (Garulf/pyFlowLauncher#44).
        if result.get("Preview") is None:
            result["Preview"] = preview(self.subtitle)
        # Flow Launcher saves these settings when the result is selected.
        if self.settings_change:
            result["SettingsChange"] = self.settings_change
        return result


def glyph(char: Optional[str]) -> Optional[Glyph]:
    if not char:
        return None
    return Glyph(Glyph=char, FontFamily=FONT)


def preview(description: Optional[str]) -> PreviewInfo:
    return PreviewInfo(PreviewImagePath=None, Description=description or "", IsMedia=False)


def make_result(title: str, subtitle: Optional[str] = None, icon_char: Optional[str] = None, **kwargs) -> HassResult:
    return HassResult(title=title, subtitle=subtitle, icon=ICON, glyph=glyph(icon_char), **kwargs)


def settings_result(title: str, subtitle: str) -> HassResult:
    return make_result(title, subtitle).add_action(api.open_setting_dialog())
