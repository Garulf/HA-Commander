import pytest

from homeassistant import MediaPlayer


def media_player(client, **attributes):
    entity = {"entity_id": "media_player.living_room", "state": "playing", "attributes": {"friendly_name": "Living Room", **attributes}}
    return client.create_entity(entity)


def test_media_player_marks_current_source(client):
    player = media_player(client, source_list=["TV", "Radio"], source="Radio")

    assert isinstance(player, MediaPlayer)
    assert player.Radio.icon == "radiobox-marked"
    assert player.TV.icon == "radiobox-blank"


@pytest.mark.parametrize("attributes", [
    {"source_list": ["TV"], "source": "Spotify Connect"},
    {"source": "uuid:7123ceda-9d21-1eb0-0080-00067886c60e"},
    {"source_list": None, "source": "iPhone"},
    {"source_list": None},
])
def test_media_player_tolerates_missing_sources(client, attributes):
    player = media_player(client, **attributes)

    current_source = attributes.get("source")
    assert isinstance(player, MediaPlayer)
    assert current_source is None or not hasattr(player, current_source)


def test_select_option_calls_select_domain(client):
    select = client.create_entity({"entity_id": "select.washer_mode", "state": "Eco", "attributes": {"options": ["Eco", "Quick"]}})

    select.Quick()

    assert client.calls[-1] == ("POST", "services/select/select_option", {"entity_id": "select.washer_mode", "option": "Quick"})


def test_input_select_option_calls_input_select_domain(client):
    input_select = client.create_entity({"entity_id": "input_select.house_mode", "state": "Home", "attributes": {"options": ["Home", "Away"]}})

    input_select.Away()

    assert client.calls[-1] == ("POST", "services/input_select/select_option", {"entity_id": "input_select.house_mode", "option": "Away"})


def test_group_member_action_toggles_that_member(client):
    group = client.create_entity({"entity_id": "group.downstairs", "state": "on", "attributes": {"entity_id": ["light.kitchen", "switch.coffee_maker"]}})

    getattr(group, "light.kitchen")()

    assert client.calls[-1] == ("POST", "services/homeassistant/toggle", {"entity_id": "light.kitchen"})
