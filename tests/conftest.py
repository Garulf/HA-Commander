import json

import pytest

import commander
from homeassistant import Client

STATES = [
    {"entity_id": "light.living_room", "state": "on", "attributes": {"friendly_name": "Living Room Lights", "effect_list": ["Rainbow"]}},
    {"entity_id": "light.kitchen", "state": "off", "attributes": {"friendly_name": "Kitchen Lights"}},
    {"entity_id": "switch.coffee_maker", "state": "off", "attributes": {"friendly_name": "Coffee Maker"}},
    {"entity_id": "cover.garage_door", "state": "closed", "attributes": {"friendly_name": "Garage Door"}},
    {"entity_id": "sensor.custom", "state": "1", "attributes": {"friendly_name": "Custom", "icon": "mdi:thermometer"}},
]
LOGBOOK = [
    {"when": "2026-10-02T18:00:00+00:00", "name": "Coffee Maker", "message": "turned off", "entity_id": "switch.coffee_maker"},
    {"when": "2026-10-02T18:05:00+00:00", "name": "Living Room Lights", "message": "turned on", "entity_id": "light.living_room"},
    {"when": "2026-10-02T18:06:00+00:00", "name": "Home Assistant", "message": "started"},
]
ERROR_LOG = "2026-10-02 18:00:00.000 WARNING first\n2026-10-02 18:01:00.000 ERROR second\n"


class FakeResponse:
    def __init__(self, payload):
        self._payload = payload

    def json(self):
        return self._payload

    @property
    def text(self):
        return self._payload


class FakeClient(Client):
    def __init__(self):
        super().__init__("http://hass.local:8123", "token")
        self.calls = []

    def request(self, method, endpoint, data=None):
        self.calls.append((method, endpoint, data))
        payloads = {"states": STATES, "logbook": LOGBOOK, "error_log": ERROR_LOG}
        return FakeResponse(json.loads(json.dumps(payloads.get(endpoint, []))))


@pytest.fixture
def settings():
    launcher = commander.plugin.launcher
    launcher._settings = {"url": "http://hass.local:8123", "token": "token", "verify_ssl": True, "max_results": "50"}
    launcher.action_keyword = "ha"
    yield launcher._settings
    launcher._settings = {}
    launcher.action_keyword = ""


@pytest.fixture
def client(settings, monkeypatch):
    fake = FakeClient()
    monkeypatch.setattr(commander, "hass", lambda: fake)
    return fake
