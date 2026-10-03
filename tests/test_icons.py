import pytest

import icons


def test_icon_accepts_names_aliases_and_mdi_prefix():
    assert icons.icon("lightbulb") == icons.icon("mdi:lightbulb") == chr(0xF0335)
    assert icons.icon("unknown-icon") is None
    assert icons.icon(None) is None


@pytest.mark.parametrize(
    ("domain", "state", "device_class", "expected"),
    [
        ("light", "on", None, "lightbulb"),
        ("light", "off", None, "lightbulb-off"),
        ("lock", "unlocked", None, "lock-open-variant"),
        ("binary_sensor", "on", "door", "door-open"),
        ("binary_sensor", "off", "door", "door-closed"),
        ("binary_sensor", "on", "made_up_class", "checkbox-marked-circle"),
        ("media_player", "playing", "tv", "television-play"),
        ("sensor", "57", "battery", "battery-50"),
        ("sensor", "4", "battery", "battery-alert"),
        ("sensor", "unknown", "battery", "battery-unknown"),
        ("sensor", "21.5", "temperature", "thermometer"),
        ("todo", "3", None, "clipboard-list"),
        ("number", "5", None, "ray-vertex"),
        ("zone", "0", None, "map-marker-radius"),
    ],
)
def test_entity_icon_matches_home_assistant(domain, state, device_class, expected):
    assert icons.entity_icon(domain, state, device_class) == icons.icon(expected)


def test_unknown_domain_has_no_entity_icon():
    assert icons.entity_icon("not_a_domain", "on") is None


def test_every_entity_action_has_an_icon():
    import inspect

    import homeassistant

    for _, cls in inspect.getmembers(homeassistant, inspect.isclass):
        if not issubclass(cls, homeassistant.BaseEntity):
            continue
        for name, member in inspect.getmembers(cls, callable):
            if getattr(member, "_service", False):
                assert icons.icon(member.icon), f"{cls.__name__}.{name}: {member.icon}"
