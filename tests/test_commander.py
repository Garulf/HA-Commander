import asyncio

import requests

import commander
import icons
from launcher import KEEP_OPEN


def titles(results):
    return [result.title for result in results]


def test_entity_search_matches_friendly_name_and_entity_id(client):
    assert titles(commander.search(client, "living")) == ["Living Room Lights"]
    assert titles(commander.search(client, "switch.")) == ["Coffee Maker"]


def test_entity_result_runs_default_action_and_has_context(client):
    result = commander.search(client, "kitchen")[0].to_json()
    assert result["JsonRPCAction"]["Method"] == "action"
    assert result["JsonRPCAction"]["Parameters"][0]["entity_id"] == "light.kitchen"
    assert result["ContextData"][0]["entity_id"] == "light.kitchen"
    assert result["Glyph"]["FontFamily"].endswith("materialdesignicons-webfont.ttf")
    assert result["Preview"] is not None


def test_brightness_hint_only_for_lights(client):
    results = commander.search(client, "kitchen 40")
    assert results[0].subtitle.endswith("40%")
    assert "Brightness" not in commander.search(client, "coffee 40")[0].subtitle


def test_hidden_entities_and_max_results(client, settings):
    settings["hidden_entities"] = ["cover.garage_door"]
    assert titles(commander.search(client, "garage")) == ["No Results Found!"]
    settings["max_results"] = "2"
    assert len(commander.search(client, "")) == 2


def test_domain_filter_changes_query_with_action_keyword(client, settings):
    result = commander.search(client, "#li")[0].to_json()
    assert result["Title"] == "light"
    assert result["JsonRPCAction"] == {"Method": "change_query", "Parameters": ["ha light."], "DontHideAfterAction": False}
    commander.plugin.launcher.action_keyword = ""
    assert commander.search(client, "#li")[0].json_rpc_action["Parameters"] == ["light."]


def test_logbook_is_newest_first(client):
    results = commander.search(client, "@")
    assert titles(results) == ["Home Assistant", "Living Room Lights", "Coffee Maker"]
    assert results[0].json_rpc_action is None
    assert results[1].json_rpc_action["Parameters"] == ["ha light.living_room"]
    assert results[0].score > results[1].score > results[2].score


def test_error_log_is_newest_first(client):
    results = commander.search(client, "!")
    assert [r.subtitle for r in results] == ["ERROR second", "WARNING first"]


def test_context_menu_lists_services_attributes_and_hide(client, settings):
    settings["hidden_entities"] = ["cover.garage_door"]
    entity = commander.search(client, "living")[0].context_data[0]
    menu = [r.to_json() for r in commander.context_menu([entity])]
    by_title = {r["Title"]: r for r in menu}
    assert {"Toggle", "Turn On", "Turn Off", "Rainbow", "Red"} <= set(by_title)
    assert by_title["Rainbow"]["JsonRPCAction"]["Parameters"] == [entity, "", "Rainbow"]
    assert by_title["light.living_room"]["JsonRPCAction"]["Method"] == "Flow.Launcher.CopyToClipboard"
    assert "None" not in by_title
    hide = menu[-1]
    assert hide["Title"] == "Hide Entity"
    assert hide["SettingsChange"] == {"hidden_entities": ["cover.garage_door", "light.living_room"]}
    assert hide["JsonRPCAction"]["Method"] == "Flow.Launcher.ShowMsg"


def test_call_service_sets_brightness_or_runs_service(client):
    kitchen = commander.search(client, "kitchen")[0].context_data[0]
    living_room = commander.search(client, "living")[0].context_data[0]
    commander.call_service(client, kitchen, "kitchen_40", "_default_action")
    commander.call_service(client, living_room, "", "Rainbow")
    commander.call_service(client, living_room, "", "_default_action")
    assert client.calls[-3:] == [
        ("POST", "services/homeassistant/turn_on", {"brightness_pct": 40, "entity_id": "light.kitchen"}),
        ("POST", "services/homeassistant/turn_on", {"effect": "Rainbow", "entity_id": "light.living_room"}),
        ("POST", "services/homeassistant/toggle", {"entity_id": "light.living_room"}),
    ]


def test_custom_mdi_icon_overrides_domain_icon(client):
    entity = client.create_entity({"entity_id": "light.desk", "state": "on", "attributes": {"icon": "mdi:robot-vacuum"}})
    assert entity._icon() == icons.icon("robot-vacuum") is not None


def test_query_without_token_asks_for_settings(settings):
    settings["token"] = ""
    results = asyncio.run(commander.query("living"))
    assert results[0].json_rpc_action["Method"] == "Flow.Launcher.OpenSettingDialog"


def test_query_reports_rejected_token(settings, monkeypatch):
    response = requests.Response()
    response.status_code = 401

    def unauthorized(client, query):
        raise requests.HTTPError(response=response)

    monkeypatch.setattr(commander, "search", unauthorized)
    results = asyncio.run(commander.query("living"))
    assert results[0].title == "Home Assistant rejected the access token"


def test_query_reports_connection_errors(settings, monkeypatch):
    def offline(client, query):
        raise requests.ConnectionError()

    monkeypatch.setattr(commander, "search", offline)
    assert asyncio.run(commander.query("x"))[0].title == "Could not connect to Home Assistant!"


def test_change_query_invokes_host_and_keeps_window_open(monkeypatch):
    sent = []

    async def invoke(command):
        sent.append(command)

    monkeypatch.setattr(commander.plugin.launcher.api, "invoke", invoke)
    assert asyncio.run(commander.change_query("ha light.")) == KEEP_OPEN
    assert sent == [{"Method": "Flow.Launcher.ChangeQuery", "Parameters": ["ha light.", False]}]


def test_hass_client_is_reused_until_settings_change(settings):
    first = commander.hass()
    assert commander.hass() is first
    settings["url"] = "http://other:8123/"
    assert commander.hass() is not first
    assert commander.hass()._url == "http://other:8123"
