# -*- coding: utf-8 -*-
import string
import os.path
import json
from configparser import ConfigParser


from flox import Flox
import requests

PLUGIN_JSON = './plugin.json'
SETTINGS = '../../Settings/Settings.json'
CONFIG_FILE = './plugin/config.ini'
DEV_CONFIG = './plugin/.dev-config.ini'
ICONS_FOLDER = './icons/icons_white/'
COLORS_FILE = './plugin/colors.json'
MAX_ITEMS = 30

with open(COLORS_FILE, 'r') as _f:
    COLORS = json.load(_f)

class Commander(Flox):

    def __init__(self):
        self._results = []
        self.load_config()
        if self.ssl:
            self.protocol = "http://"
        else:
            self.protocol = "https://"
        self.url = f"{self.protocol}{self.host}:{self.port}/"
        self.headers = {
            "Authorization": f"Bearer {self.token}",
            "content-type": "application/json",
        }
        self.session = requests.Session()
        super().__init__()

    def load_config(self):
        config = ConfigParser()
        config_file = CONFIG_FILE
        if os.path.exists(DEV_CONFIG):
            config_file = DEV_CONFIG
        config.read(config_file)
        _section = config.sections()[0]
        self.host = config[_section]['host']
        self.port = config[_section]['port']
        self.token = config[_section]['token']
        self.ssl = config[_section]['ssl']
        self.verify_ssl = config[_section]['verify_ssl']
        self.max_items = config[_section].get('max_items', MAX_ITEMS)

    

    def request(self, method, endpoint, data=None):
        url = f"{self.url}api/{endpoint}"
        if data:
            data = json.dumps(data)
        response = self.session.request(method, url, headers=self.headers, data=data, verify=self.verify_ssl, timeout=60)
        response.raise_for_status()
        return response.json()

    def states(self):
        return self.request('GET', 'states')

    def entity_state(self, entity_id):
        endpoint = f"states/{entity_id}"
        return self.request('GET', endpoint)

    def call_services(self, domain, service, data):
        endpoint = f"services/{domain}/{service}"
        return self.request('POST', endpoint, data)

    @staticmethod
    def domain(entity_id, domain=None):
        _entity_domain = entity_id.split('.')[0]
        if not domain:
            return _entity_domain
        if _entity_domain == domain:
            return True
        else:
            return False

    def hvac_next_mode(self, entity_id):
        entity = self.entity_state(entity_id)
        modes = entity['attributes']['hvac_modes']
        for idx, mode in enumerate(modes):
            if mode == entity['state']:
                new_mode = idx + 1
                if mode == modes[-1]:
                    new_mode = 0
                self.call_services('climate', 'set_hvac_mode', {'entity_id': entity_id, 'hvac_mode': modes[new_mode]})


    def toggle(self, entity_id):
        data = {
            "entity_id": entity_id
        }
        # Locks CANNOT be toggle with homeassistant domain
        if entity_id.startswith("lock"):
            lock_state = self.entity_state(entity_id)['state']
            if lock_state == "locked":
                self.call_services("lock", "unlock", {"entity_id": entity_id})
            else:
                self.call_services("lock", "lock", {"entity_id": entity_id})
        else:
            self.call_services('homeassistant', 'toggle', data=data)

    def turn_on(self, entity_id, color_name=None, effect=None, **service_data):
        service_data['entity_id'] = entity_id
        if color_name:
            service_data['color_name'] = color_name
        if effect:
            service_data['effect'] = effect
        self.call_services('light', 'turn_on', service_data)

    def play_pause(self, entity_id):
        data = {
            "entity_id": entity_id
        }
        self.call_services('media_player', 'media_play_pause', data=data)

    def get_icon(self, icon):
        if icon is None or not os.path.exists(icon):
            if os.path.exists(f"{ICONS_FOLDER}{icon}.png"):
                icon = f"{ICONS_FOLDER}{icon}.png"
            else:
                icon = self.icon
        return icon

    def context_menu(self, data):
        entity_attributes = data[0].pop('attributes', {})
        entity = {**data[0], **entity_attributes}
        for item in entity:
            self.add_item(
                title=str(entity[item]),
                subtitle=item,
                icon=f"{ICONS_FOLDER}info.png",
            )
        if self.domain(entity['entity_id'], 'light'):
            for color in COLORS:
                self.add_item(
                    title=color.title(),
                    subtitle='Press ENTER to change to this color',
                    icon=self.get_icon("palette"),
                    method="turn_on",
                    parameters=[entity['entity_id'], color]
                )
            for effect in entity_attributes['effect_list']:
                self.add_item(
                    title=effect,
                    icon=self.get_icon("playlist-play"),
                    method="turn_on",
                    parameters=[entity['entity_id'], None, effect]
                )
        if self.domain(entity['entity_id'], 'climate'):
            for mode in entity_attributes['hvac_modes']:
                self.add_item(
                    title=mode.title(),
                    subtitle='Press ENTER to change to this mode',
                    icon=self.get_icon("order-bool-descending"),
                    method="call_services",
                    parameters=['climate', 'set_hvac_mode', {'entity_id': entity['entity_id'], 'hvac_mode': mode}]
                )
        return self._results

    def query(self, query):

        q = query.lower().replace(' ', '_')
        fq = q.rstrip('_' + string.digits)
        states = self.states()
        for entity in states:
            friendly_name = entity['attributes'].get('friendly_name', '')
            entity_id = entity['entity_id']
            if fq in entity_id.lower() or fq in friendly_name.lower().replace(' ', '_'):
                domain = self.domain(entity_id)
                state = entity['state']
                icon_string = f"{domain}_{state}"
                icon = domain
                if os.path.exists(f"{ICONS_FOLDER}{icon_string}.png"):
                    icon = icon_string
                subtitle = f"[{domain}] {state}"
                if q.split('_')[-1].isdigit() and self.domain(entity_id, 'light'):
                    subtitle = f"{subtitle} - Press ENTER to change brightness to: {q.split('_')[-1]}%"
                self.add_item(
                    title=f"{friendly_name or entity_id}",
                    subtitle=subtitle,
                    icon=self.get_icon(icon),
                    context=[entity],
                    method="action",
                    parameters=[entity_id, q]
                )
            if len(self._results) > MAX_ITEMS:
                break
            

        if len(self._results) == 0:
            self.add_item(
                title="No Results Found!"
            )
        return self._results[:5]

    def action(self, entity_id, q):
        # API.start_loadingbar()
        if self.domain(entity_id, 'light') and q.split('_')[-1].isdigit():
            self.turn_on(entity_id, brightness_pct=int(q.split('_')[-1]))
        elif self.domain(entity_id, 'media_player'):
            self.play_pause(entity_id)
        elif self.domain(entity_id, 'climate'):
            self.hvac_next_mode(entity_id)
        else:
            self.toggle(entity_id)

if __name__ == "__main__":
    Commander()
