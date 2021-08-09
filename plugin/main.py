# -*- coding: utf-8 -*-
import string
import os.path
import json
from configparser import ConfigParser


from flox import Flox
from hass import HomeAssistant

PLUGIN_JSON = "./plugin.json"
SETTINGS = "../../Settings/Settings.json"
CONFIG_FILE = "./plugin/config.ini"
DEV_CONFIG = "./plugin/.dev-config.ini"
ICONS_FOLDER = "./icons/icons_white/"
COLORS_FILE = "./plugin/colors.json"
MAX_ITEMS = 30

with open(COLORS_FILE, "r") as _f:
    COLORS = json.load(_f)


class Commander(Flox):
    def __init__(self):
        self._results = []
        self.load_config()
        if self._ssl:
            self._protocol = "http://"
        else:
            self._protocol = "https://"
        self.hass = HomeAssistant(
            self._protocol, self._host, self._port, self._token, self._verify_ssl
        )
        super().__init__()

    def load_config(self):
        config = ConfigParser()
        config_file = CONFIG_FILE
        if os.path.exists(DEV_CONFIG):
            config_file = DEV_CONFIG
        config.read(config_file)
        _section = config.sections()[0]
        self._host = config[_section]["host"]
        self._port = config[_section]["port"]
        self._token = config[_section]["token"]
        self._ssl = config[_section]["ssl"]
        self._verify_ssl = config[_section]["verify_ssl"]
        self._max_items = config[_section].get("max_items", MAX_ITEMS)

    def get_icon(self, icon):
        if icon is None or not os.path.exists(icon):
            if os.path.exists(f"{ICONS_FOLDER}{icon}.png"):
                icon = f"{ICONS_FOLDER}{icon}.png"
            else:
                icon = self.icon
        return icon

    def context_menu(self, data):
        entity_attributes = data[0].pop("attributes", {})
        entity = {**data[0], **entity_attributes}
        for item in entity:
            self.add_item(
                title=str(entity[item]),
                subtitle=item,
                icon=f"{ICONS_FOLDER}info.png",
            )
        if self.hass.domain(entity["entity_id"], "light"):
            for color in COLORS:
                self.add_item(
                    title=color.title(),
                    subtitle="Press ENTER to change to this color",
                    icon=self.get_icon("palette"),
                    method="turn_on",
                    parameters=[entity["entity_id"], color],
                )
            for effect in entity_attributes["effect_list"]:
                self.add_item(
                    title=effect,
                    icon=self.get_icon("playlist-play"),
                    method="turn_on",
                    parameters=[entity["entity_id"], None, effect],
                )
        return self._results

    def query(self, query):

        q = query.lower().replace(" ", "_")
        fq = q.rstrip("_" + string.digits)
        states = self.hass.states()
        for entity in states:
            friendly_name = entity["attributes"].get("friendly_name", "")
            entity_id = entity["entity_id"]
            if fq in entity_id.lower() or fq in friendly_name.lower().replace(" ", "_"):
                domain = self.hass.domain(entity_id)
                state = entity["state"]
                icon_string = f"{domain}_{state}"
                icon = domain
                if os.path.exists(f"{ICONS_FOLDER}{icon_string}.png"):
                    icon = icon_string
                subtitle = f"[{domain}] {state}"
                if q.split("_")[-1].isdigit() and self.hass.domain(entity_id, "light"):
                    subtitle = f"{subtitle} - Press ENTER to change brightness to: {q.split('_')[-1]}%"
                self.add_item(
                    title=f"{friendly_name or entity_id}",
                    subtitle=subtitle,
                    icon=self.get_icon(icon),
                    context=[entity],
                    method="action",
                    parameters=[entity_id, q],
                )
            if len(self._results) > MAX_ITEMS:
                break

        if len(self._results) == 0:
            self.add_item(title="No Results Found!")
        return self._results[:5]

    def action(self, entity_id, q):
        # API.start_loadingbar()
        if self.hass.domain(entity_id, "light") and q.split("_")[-1].isdigit():
            self.hass.turn_on(entity_id, brightness_pct=int(q.split("_")[-1]))
        elif self.hass.domain(entity_id, "climate"):
            self.hass.call_services(
                "climate",
                "set_hvac_mode",
                {"entity_id": entity_id, "hvac_mode": "cool"},
            )
        elif self.hass.domain(entity_id, "media_player"):
            self.hass.play_pause(entity_id)
        else:
            self.hass.toggle(entity_id)


if __name__ == "__main__":
    Commander()
