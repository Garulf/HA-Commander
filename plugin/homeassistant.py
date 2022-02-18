import os
import json
from functools import partial, wraps
import webbrowser
import logging

import requests
from requests.exceptions import ConnectionError, HTTPError

from icons import DEFAULT_ICONS

log = logging.getLogger(__name__)

COLORS_FILE = "./plugin/colors.json"
META_FILE = "./meta.json"
with open(META_FILE, "r") as f:
    ICONS = json.load(f)
with open(COLORS_FILE, "r") as _f:
    COLORS = json.load(_f)


def format_name(name):
    return name.replace("_", " ").title()


def service(icon=None, score=0):
    def decorator(func):
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            return func(self, *args, **kwargs)

        wrapper.icon = getattr(func, "icon", icon or func.__name__)
        wrapper.score = getattr(func, "score", score)
        wrapper._service = True
        wrapper.name = format_name(func.__name__)
        return wrapper

    return decorator


def action():
    def decorator(func):
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            return func(self, *args, **kwargs)

        wrapper._action = True
        return wrapper

    return decorator


class Base(object):
    def __init__(self, url, token, verify_ssl):
        self._url = f"{url}"
        self._headers = {
            "Authorization": f"Bearer {token}",
            "content-type": "application/json",
        }
        self._cacert = os.path.join(
            os.path.abspath(os.path.dirname(os.path.dirname(__file__))),
            "lib",
            "certifi",
            "cacert.pem",
        )
        self._verify_ssl = verify_ssl
        if self._verify_ssl:
            self._verify_ssl = self._cacert
        self._session = requests.Session()

    def request(self, method, endpoint, data=None):
        url = f"{self._url}/api/{endpoint}"
        if data:
            data = json.dumps(data)
        response = self._session.request(
            method,
            url,
            headers=self._headers,
            data=data,
            verify=self._verify_ssl,
            timeout=20,
        )
        response.raise_for_status()
        return response

    def grab_icon(self, domain, state="on"):
        if state == "unavailable":
            icon = DEFAULT_ICONS["unavailable"]
        elif domain is None:
            icon = DEFAULT_ICONS["broken_image"]
        if not domain in DEFAULT_ICONS.keys():
            return self.lookup_icon(domain)
        else:
            icon_name = f"{domain}_{state}".lower()
            icon = DEFAULT_ICONS.get(icon_name) or DEFAULT_ICONS.get(domain)
        if icon:
            return chr(int(icon, 16))
        return None

    def lookup_icon(self, name):
        for _icon in ICONS:
            if name == _icon["name"]:
                return chr(int(_icon["codepoint"], 16))
        return None


class Client(Base):
    def __init__(self, url, token, verify_ssl=True):
        super().__init__(url, token, verify_ssl)

    def api(self):
        return self.request("GET", "")

    def states(self):
        entities = []
        _states = self.request("GET", "states").json()
        for entity in _states:
            entities.append(self.create_entity(entity))
        return entities

    def get_domains(self, entities):
        domains = []
        for entity in entities:
            domains.append(entity.domain.lower())
        return sorted(list(set(domains)))

    def logbook(self, date=None):
        endpoint = "logbook"
        return self.request("GET", endpoint).json()

    def error_log(self):
        endpoint = "error_log"
        return self.request("GET", endpoint).text.splitlines()

    def camera_proxy(self, entity_id):
        endpoint = "camera_proxy"
        return self.request("GET", endpoint, {"entity_id": entity_id}).content

    def create_entity(self, entity):
        _domain = entity["entity_id"].split(".")[0]
        _cls = globals().get(_domain.replace("_", " ").title().replace(" ", ""), Entity)
        if type(_cls) == type(Entity):
            return _cls(self, entity)

    def entity_state(self, entity_id):
        endpoint = f"states/{entity_id}"
        return self.request("GET", endpoint).json()

    def call_services(self, domain, service, data):
        endpoint = f"services/{domain}/{service}"
        return self.request("POST", endpoint, data).json()

    @staticmethod
    def domain(entity_id, domain=None):
        _entity_domain = entity_id.split(".")[0]
        if not domain:
            return _entity_domain
        if _entity_domain == domain:
            return True
        else:
            return False

    def turn_on(self, entity_id, color_name=None, effect=None, **service_data):
        service_data["entity_id"] = entity_id
        if color_name:
            service_data["color_name"] = color_name
        if effect:
            service_data["effect"] = effect
        self.call_services("light", "turn_on", service_data)


class BaseEntity(object):
    def __init__(self, client, entity):
        self._client = client
        self._entity = entity
        self.entity_id = entity.get("entity_id")
        self.domain = self.entity_id.split(".")[0]
        self.name = entity.get("name")
        self.friendly_name = entity.get("attributes", "").get("friendly_name", "")
        self.state = entity.get("state")
        self.attributes = entity["attributes"]
        self.target = {"entity_id": self.entity_id}
        # for attribute in entity['attributes']:
        #     setattr(self, attribute, entity['attributes'][attribute])

    def _as_dict(self) -> dict:
        """Return dictionary representation of entity."""
        return self._entity

    def _icon(self):
        icon = self._client.grab_icon(self.domain, self.state)
        if not icon and self.attributes.get("icon"):
            with open(META_FILE, "r") as f:
                for _icon in json.load(f):
                    if self.attributes["icon"] == _icon["name"]:
                        icon = chr(int(self.attributes["icon"], 16))
                        break
        return icon

    def _update(self):
        self.__init__(self._client, self._client.entity_state(self.entity_id))


class Entity(BaseEntity):
    """Representation of a generic entity."""

    def __init__(self, client, entity):
        super().__init__(client, entity)

    def __call__(self):
        self._default_action()

    def _default_action(self):
        """Default action for entity."""
        self.toggle()

    @service(icon="swap-horizontal-bold", score=150)
    def toggle(self, domain="homeassistant") -> None:
        """Toggle entity."""
        self._client.call_services(domain, "toggle", data=self.target)

    @service(icon="switch", score=100)
    def turn_on(self, **service_data) -> any:
        """Turn entity on."""
        for arg in service_data:
            service_data[arg] = service_data[arg]
        service_data["entity_id"] = self.entity_id
        self._client.call_services("homeassistant", "turn_on", data=service_data)

    @service(icon="switch_off", score=100)
    def turn_off(self, **service_data) -> None:
        """Turn entity off."""
        for arg in service_data:
            service_data[arg] = service_data[arg]
        service_data["entity_id"] = self.entity_id
        self._client.call_services("homeassistant", "turn_off", data=service_data)


class Light(Entity):
    """Representation of a Light entity."""

    def __init__(self, client: Client, entity: dict) -> None:
        super().__init__(client, entity)
        for color in COLORS:
            setattr(self, f"{color}", partial(self._set_color, color=color))
            getattr(self, f"{color}").name = color.title()
            getattr(self, f"{color}").__doc__ = f"Set light color to {color}."
            getattr(self, f"{color}").icon = "palette"
            getattr(self, f"{color}").score = 0
        for effect in self.attributes.get("effect_list", []):
            setattr(self, f"{effect}", partial(self.turn_on, effect=effect))
            getattr(self, f"{effect}").name = effect.title()
            getattr(self, f"{effect}").__doc__ = f"Set light effect to {effect}."
            getattr(self, f"{effect}").icon = "star-circle-outline"
            getattr(self, f"{effect}").score = 0
            # print(getattr(self, f"{color}").__icon__)

    def _set_color(self, color: str) -> None:
        self.turn_on(**{"color_name": color})

    def _set_effect(self, effect: str) -> None:
        self.turn_on(**{"effect": effect})

    def _brightness_pct(self, brightness_pct: int) -> None:
        """Set brightness of light."""
        self.turn_on(**{"brightness_pct": brightness_pct})

    def _color(self, color_name: str) -> None:
        """Return the color of the light."""
        self.turn_on(color_name=color_name)

    def _effect(self, effect: str) -> None:
        """Change light effect."""
        self.turn_on(effect=effect)


class Lock(BaseEntity):
    """Representation of a Lock entity."""

    def __init__(self, client: Client, entity: dict) -> None:
        super().__init__(client, entity)

    def _default_action(self):
        """Default action for entity."""
        self.toggle()

    @service(icon="lock")
    def lock(self, **service_data) -> None:
        """Lock the entity."""
        self._client.call_services("lock", "lock", data=self.target)

    @service(icon="lock-open")
    def unlock(self, **service_data) -> None:
        self._client.call_services("lock", "unlock", data=self.target)

    @service(icon="swap-horizontal-bold")
    def toggle(self) -> None:
        """Toggle the lock (Locked/Unlocked)."""
        # Generic toggle does not work for locks
        lock_state = self._client.entity_state(self.entity_id)["state"]
        data = {"entity_id": self.entity_id}
        if lock_state == "locked":
            self._client.call_services("lock", "unlock", data)
        else:
            self._client.call_services("lock", "lock", data)


class MediaPlayer(Entity):
    """Representation of a Media Player entity."""

    def __init__(self, client: Client, entity: dict) -> None:
        super().__init__(client, entity)
        for source in self.attributes.get("source_list", []):
            setattr(self, source, partial(self._select_source, source))
            getattr(self, source).name = source
            getattr(self, source).__doc__ = 'Set Source to "{}"'.format(source)
            getattr(self, source).icon = "radiobox-blank"
        current_source = self.attributes.get("source")
        if current_source:
            getattr(self, current_source).icon = "radiobox-marked"
            getattr(self, current_source).__doc__ = "Currently selected Source."

    @service(icon="arrow-right")
    def _select_source(self, source) -> None:
        """Select source."""
        data = self.target
        data["source"] = source
        self._client.call_services("media_player", "select_source", data=data)

    @service(icon="play")
    def play(self) -> None:
        """Coninue Playing media."""
        self._client.call_services("media_player", "media_play", self.target)

    @service(icon="pause")
    def pause(self) -> None:
        """Pause currently playing media."""
        self._client.call_services("media_player", "media_pause", data=self.target)

    @service(icon="play-pause")
    def play_pause(self) -> None:
        """Toggle Play/Pause."""
        self._client.call_services("media_player", "media_play_pause", data=self.target)


class Climate(Entity):
    """Representation of a Climate entity."""

    def __init__(self, client: Client, entity: dict) -> None:
        super().__init__(client, entity)
        self.hvac_modes = self._entity["attributes"].get("hvac_modes", [])

    def _default_action(self):
        self.cycle_mode()

    def cycle_mode(self) -> None:
        """Cycle HVAC mode."""
        self._update()
        mode_index = self.hvac_modes.index(self.state) + 1
        if mode_index == len(self.hvac_modes):
            mode_index = 0
        service_data = self.target
        service_data["hvac_mode"] = self.hvac_modes[mode_index]
        self._client.call_services("climate", "set_hvac_mode", data=service_data)


class Script(Entity):
    """Representation of a Script entity."""

    def __init__(self, client: Client, entity: dict) -> None:
        super().__init__(client, entity)

    def _default_action(self):
        self.run()

    @service(icon="script-text-play")
    def run(self) -> None:
        """Run script."""
        self._client.call_services("script", "turn_on", data=self.target)


class Automation(Entity):
    """Representation of a Automation entity."""

    def __init__(self, client: Client, entity: dict) -> None:
        super().__init__(client, entity)
        self.__doc__ = self.state

    def _default_action(self):
        self.run()

    @service(icon="script-text-play")
    def run(self) -> None:
        """Run automation."""
        self._client.call_services("automation", "turn_on", data=self.target)


class Camera(BaseEntity):
    """Representation of a Camera entity."""

    def __init__(self, client: Client, entity: dict) -> None:
        super().__init__(client, entity)

    def _default_action(self):
        self.view()

    @service(icon="camera-image")
    def snapshot(self) -> None:
        """Take snapshot."""
        self._client.call_services("camera", "snapshot", data=self.target)

    @service(icon="television")
    def view(self) -> None:
        """View a still from this Camera entity."""
        webbrowser.open(f'{self._client._url}{self.attributes["entity_picture"]}')


class InputSelect(BaseEntity):
    """Representation of a Input_select entity."""

    def __init__(self, client: Client, entity: dict) -> None:
        super().__init__(client, entity)
        for option in self.attributes["options"]:
            setattr(self, option, partial(self._select, option))
            getattr(self, option).name = option
            getattr(self, option).__doc__ = 'Set option to "{}"'.format(option)
            getattr(self, option).icon = "radiobox-blank"
            if option == self.state:
                getattr(self, option).icon = "radiobox-marked"
                getattr(self, option).__doc__ = "Currently selected option."

    @service(icon="arrow-right")
    def _select(self, option) -> None:
        """Select option."""
        data = self.target
        data["option"] = option
        self._client.call_services("input_select", "select_option", data=data)


class Select(BaseEntity):
    def __init__(self, client: Client, entity: dict) -> None:
        super().__init__(client, entity)
        for option in self.attributes["options"]:
            setattr(self, option, partial(self._select, option))
            getattr(self, option).name = option
            getattr(self, option).__doc__ = 'Set option to "{}"'.format(option)
            getattr(self, option).icon = "radiobox-blank"
            if option == self.state:
                getattr(self, option).icon = "radiobox-marked"
                getattr(self, option).__doc__ = "Currently selected option."

    @service(icon="arrow-right")
    def _select(self, option) -> None:
        """Select option."""
        data = self.target
        data["option"] = option
        self._client.call_services("input_select", "select_option", data=data)


class Group(Entity):
    def __init__(self, client: Client, entity: dict) -> None:
        super().__init__(client, entity)
        for entity in self.attributes.get("entity_id", []):
            setattr(self, entity, partial(self.toggle, entity))
            getattr(self, entity).name = entity
            getattr(self, entity).__doc__ = 'Toggle entity "{}"'.format(entity)
            getattr(self, entity).icon = "checkbox-multiple-blank"
            getattr(self, entity)._service = True
