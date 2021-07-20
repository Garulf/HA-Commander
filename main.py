# -*- coding: utf-8 -*-
import os.path
import json
from configparser import ConfigParser

import requests

try:
    from wox import Wox as FlowLauncher
    from wox import WoxAPI as API
    PRETEXT = 'Wox'
except ModuleNotFoundError:
    from flowlauncher import FlowLauncher
    from flowlauncher import FlowLauncherAPI as API
    PRETEXT = 'Flow.Launcher'


CONFIG_FILE = './config.ini'
DEV_CONFIG = './.dev-config.ini'
ICONS_FOLDER = './icons/icons_white/'


class Commander(FlowLauncher):

    def __init__(self):
        self.results = []
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

    def request(self, method, endpoint, data=None):
        url = f"{self.url}api/{endpoint}"
        if data:
            data = json.dumps(data)
        response = self.session.request(method, url, headers=self.headers, data=data, verify=self.verify_ssl)
        response.raise_for_status()
        return response.json()

    def states(self):
        return self.request('GET', 'states')

    def entity_state(self, entity_id):
        endpoint = f"states/{entity_id}"
        return self.request('GET', endpoint)

    def services(self, domain, service, data):
        endpoint = f"services/{domain}/{service}"
        return self.request('POST', endpoint, data)

    def toggle(self, entity_id):
        data = {
            "entity_id": entity_id
        }
        # Locks CANNOT be toggle with homeassistant domain
        if entity_id.startswith("lock"):
            lock_state = self.entity_state(entity_id)['state']
            if lock_state == "locked":
                self.services("lock", "unlock", {"entity_id": entity_id})
            else:
                self.services("lock", "lock", {"entity_id": entity_id})
        else:
            self.services('homeassistant', 'toggle', data=data)

    def play_pause(self, entity_id):
        data = {
            "entity_id": entity_id
        }
        self.services('media_player', 'media_play_pause', data=data)        

    def context_menu(self, data):
        results = []
        results.append({
            "Title": data,
            "SubTitle": "test",
            #"IcoPath":ico,
            "JsonRPCAction": {
                #change query to show only service type
                "method": "Wox.ChangeQuery",
                "parameters": ["ha", False],
                # hide the query wox or not
                "dontHideAfterAction": True
            }
        })
        return results

    def query(self, query):
        q = query.lower()
        states = self.states()
        for entity in states:
            friendly_name = entity['attributes'].get('friendly_name', '')
            entity_id = entity['entity_id']
            domain = entity_id.split('.')[0]
            state = entity['state']
            icon_string = f"{domain}_{state}"
            icon = f"{ICONS_FOLDER}{domain}.png"
            if os.path.exists(f"{ICONS_FOLDER}{icon_string}.png"):
                icon = f"{ICONS_FOLDER}{icon_string}.png"
            if q in entity_id.lower() or q in friendly_name.lower():
                self.results.append({
                    "Title": f"{friendly_name or entity_id}",
                    "SubTitle": f"[{domain}] {state}",
                    "IcoPath": icon,
                    "JsonRPCAction": {
                        "method": "action",
                        "parameters": [entity_id],
                        "dontHideAfterAction": False
                    }
                })
            if len(self.results) > 30:
                break
            

        if len(self.results) == 0:
            self.results.append({
                    "Title": "No Results Found!",
                    "SubTitle": "",
                    "IcoPath": f"{ICONS_FOLDER}light_off.png",
                })
        return self.results

    def action(self, entity_id):
        API.start_loadingbar()
        if entity_id.startswith("media_player."):
            self.play_pause(entity_id)
        else:
            self.toggle(entity_id)

if __name__ == "__main__":
    Commander()
