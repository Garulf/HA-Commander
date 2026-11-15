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
