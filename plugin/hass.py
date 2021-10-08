import os
import sys
import json

import requests

class HomeAssistant(object):
    def __init__(self, protocol, host, port, token, verify_ssl=True):
        self._url = f"{protocol}{host}:{port}/"
        self._headers = {
            "Authorization": f"Bearer {token}",
            "content-type": "application/json",
        }
        self._cacert = os.path.join(os.path.abspath(os.path.dirname(os.path.dirname(__file__))), "lib", "certifi", "cacert.pem")
        self._verify_ssl = verify_ssl
        if self._verify_ssl:
            self._verify_ssl = self._cacert
        self._session = requests.Session()


    def request(self, method, endpoint, data=None):
        url = f"{self._url}api/{endpoint}"
        if data:
            data = json.dumps(data)
        response = self._session.request(
            method,
            url,
            headers=self._headers,
            data=data,
            verify=self._verify_ssl,
            timeout=60,
        )
        response.raise_for_status()
        return response.json()

    def states(self):
        return self.request("GET", "states")

    def entity_state(self, entity_id):
        endpoint = f"states/{entity_id}"
        return self.request("GET", endpoint)

    def call_services(self, domain, service, data):
        endpoint = f"services/{domain}/{service}"
        return self.request("POST", endpoint, data)

    @staticmethod
    def domain(entity_id, domain=None):
        _entity_domain = entity_id.split(".")[0]
        if not domain:
            return _entity_domain
        if _entity_domain == domain:
            return True
        else:
            return False

    def toggle(self, entity_id):
        data = {"entity_id": entity_id}
        # Locks CANNOT be toggle with homeassistant domain
        if entity_id.startswith("lock"):
            lock_state = self.entity_state(entity_id)["state"]
            if lock_state == "locked":
                self.call_services("lock", "unlock", {"entity_id": entity_id})
            else:
                self.call_services("lock", "lock", {"entity_id": entity_id})
        else:
            self.call_services("homeassistant", "toggle", data=data)

    def turn_on(self, entity_id, color_name=None, effect=None, **service_data):
        service_data["entity_id"] = entity_id
        if color_name:
            service_data["color_name"] = color_name
        if effect:
            service_data["effect"] = effect
        self.call_services("light", "turn_on", service_data)

    def play_pause(self, entity_id):
        data = {"entity_id": entity_id}
        self.call_services("media_player", "media_play_pause", data=data)
