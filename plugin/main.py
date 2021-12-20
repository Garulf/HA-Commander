# -*- coding: utf-8 -*-
import string
import os.path
import json


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


def match(query, entity, friendly_name):
    fq = query.rstrip("_" + string.digits)
    if fq in entity.lower().replace(".", "_") or fq in friendly_name.lower().replace(" ", "_"):
        return True
    return False

class Commander(Flox):

    def init_hass(self):
        self.hass = HomeAssistant(
            self.settings.get('url'), self.settings.get('token'), self.settings.get('verify_ssl')
        )

    def get_icon(self, domain, state=None):
        if state == "unavailable":
            return os.path.join(ICONS_FOLDER, "alert.png")
        domain_state_icon = os.path.join(ICONS_FOLDER, f"{domain}_{state}.png")
        domain_icon = os.path.join(ICONS_FOLDER, f"{domain}.png")
        if os.path.exists(domain_state_icon):
            return domain_state_icon
        elif os.path.exists(domain_icon):
            return domain_icon
        return self.icon

    def query(self, query):
        self.init_hass()
        q = query.lower().replace(" ", "_")
        states = self.hass.states()
        for entity in states:
            if match(q, entity.entity_id, entity.friendly_name):
                subtitle = f"[{entity.domain}] {entity.state}"
                if q.split("_")[-1].isdigit() and self.hass.domain(entity.entity_id, "light"):
                    subtitle = f"{subtitle} - Press ENTER to change brightness to: {q.split('_')[-1]}%"
                self.add_item(
                    title=f"{entity.friendly_name or entity.entity_id}",
                    subtitle=subtitle,
                    icon=self.get_icon(entity.domain, entity.state),
                    context=[entity._entity],
                    method="action",
                    parameters=[entity._entity, q],
                )
            if len(self._results) > MAX_ITEMS:
                break

        if len(self._results) == 0:
            self.add_item(title="No Results Found!")
            
    def context_menu(self, data):
        self.init_hass()
        entity = self.hass.create_entity(data[0])
        if self.hass.domain(entity.entity_id, "light"):
            for color in COLORS:
                self.add_item(
                    title=color.title(),
                    subtitle="Press ENTER to change to this color",
                    icon=self.get_icon("palette"),
                    method=self.change_color,
                    parameters=[entity._entity, color],
                )
            for effect in entity.attributes["effect_list"]:
                self.add_item(
                    title=effect,
                    icon=self.get_icon("playlist-play"),
                    method=self.effect,
                    parameters=[entity._entity, effect],
                )
        return self._results

    def action(self, entity_id, q):
        self.init_hass()
        entity = self.hass.create_entity(entity_id)
        if self.hass.domain(entity.entity_id, "light") and q.split("_")[-1].isdigit():
            entity.brightness = int(q.split("_")[-1])
        else:
            entity.default_action()

    def change_color(self, entity, color):
        self.init_hass()
        entity = self.hass.create_entity(entity)
        entity.color(color)

    def effect(self, entity, effect):
        self.init_hass()
        entity = self.hass.create_entity(entity)
        entity.effect(effect)


if __name__ == "__main__":
    Commander()
