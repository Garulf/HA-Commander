import os
import json

import requests
from requests.exceptions import ConnectionError, HTTPError

class Base(object):

    def __init__(self, url, token, verify_ssl):
        self._url = f"{url}"
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
        try:
            url = f"{self._url}/api/{endpoint}"
            if data:
                data = json.dumps(data)
            response = self._session.request(
                method,
                url,
                headers=self._headers,
                data=data,
                verify=self._verify_ssl,
                timeout=3,
            )
            response.raise_for_status()
        except (ConnectionError, HTTPError):
            raise
        else:
            return response.json()
class HomeAssistant(Base):

    def __init__(self, url, token, verify_ssl=True):
        super().__init__(url, token, verify_ssl)

    def states(self):
        entities = []
        _states = self.request("GET", "states")
        for entity in _states:
            entities.append(self.create_entity(entity))
        return entities
            
    def create_entity(self, entity):
        _domain = entity['entity_id'].split(".")[0]
        _cls = globals().get(_domain.replace("_", " ").title().replace(" ", ""), Entity)
        if type(_cls) == type(Entity):
            return _cls(self, entity)

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

    def turn_on(self, entity_id, color_name=None, effect=None, **service_data):
        service_data["entity_id"] = entity_id
        if color_name:
            service_data["color_name"] = color_name
        if effect:
            service_data["effect"] = effect
        self.call_services("light", "turn_on", service_data)



class Entity(object):
    """Representation of a generic entity."""
    
    def __init__(self, HomeAssistant, entity):
        self.HomeAssistant = HomeAssistant
        self._entity = entity
        self.entity_id = entity.get("entity_id")
        self.domain = self.entity_id.split(".")[0]
        self.name = entity.get('name')
        self.friendly_name = entity.get('attributes', "").get('friendly_name', "")
        self.state = entity.get('state')
        self.attributes = entity['attributes']
        self.target = {"entity_id": self.entity_id}

    def default_action(self):
        """Default action for entity."""
        self.toggle()

    def toggle(self, domain="homeassistant") -> None:
        """Gernic toggle method."""
        self.HomeAssistant.call_services(domain, "toggle", data=self.target)

    def turn_on(self, **service_data) -> any:
        """Generic turn on method."""
        for arg in service_data:
            service_data[arg] = service_data[arg]
        service_data["entity_id"] = self.entity_id
        self.HomeAssistant.call_services("homeassistant", "turn_on", data=service_data)

    def turn_off(self, **service_data) -> None:
        """Generic turn off method."""
        for arg in service_data:
            service_data[arg] = service_data[arg]
        service_data["entity_id"] = self.entity_id
        self.HomeAssistant.call_services("homeassistant", "turn_off", data=service_data)

    def update(self):
        self.__init__(self.HomeAssistant, self.HomeAssistant.entity_state(self.entity_id))

class Light(Entity):
    """Representation of a Light entity."""

    def __init__(self, HomeAssistant: HomeAssistant, entity: dict) -> None:
        super().__init__(HomeAssistant, entity)
        self._brightness = self._entity.get("brightness", 0)
        self._brightness_pct = (self._entity.get("brightness", 0) * 255) / 100

    @property
    def brightness(self) -> int:
        """Return the brightness of this light between 0..255."""
        return self._brightness

    @brightness.setter
    def brightness(self, brightness):
        """Change light brightness"""
        service_data = self.target
        service_data["brightness"] = brightness
        self.HomeAssistant.call_services("light", "turn_on", service_data)
        self._brightness = brightness

    @property
    def brightness_pct(self) -> float:
        """Return the brightness of the light."""
        return (self._entity.get("brightness", 0) * 50) / 100

    @brightness_pct.setter
    def brightness_pct(self, brightness: float) -> None:
        """Set the brightness of the light."""
        self.HomeAssistant.call_services("light", "turn_on", data={"entity_id": self.entity_id, "brightness_pct": brightness})
        self._brightness = (brightness / 100) * 255

    def color(self, color_name: str) -> None:
        """Return the color of the light."""
        self.turn_on(color_name=color_name)

    def effect(self, effect: str) -> None:
        """Return the effect of the light."""
        self.turn_on(effect=effect)

class Lock(Entity):
    """Representation of a Lock entity."""

    def __init__(self, HomeAssistant: HomeAssistant, entity: dict) -> None:
        super().__init__(HomeAssistant, entity)

    def turn_on(self):
        return super().turn_on()

    def toggle(self) -> None:
        """Toggle the lock state."""
        # Generic toggle does not work for locks
        lock_state = self.HomeAssistant.entity_state(self.entity_id)["state"]
        data = {"entity_id": self.entity_id}
        if lock_state == "locked":
            self.HomeAssistant.call_services("lock", "unlock", data)
        else:
            self.HomeAssistant.call_services("lock", "lock", data)

class MediaPlayer(Entity):
    """Representation of a Media Player entity."""

    def __init__(self, HomeAssistant: HomeAssistant, entity: dict) -> None:
        super().__init__(HomeAssistant, entity)

    def play(self) -> None:
        """Service: Play media."""
        self.HomeAssistant.call_services("media_player", "media_play", self.target)

    def pause(self) -> None:
        """Pause media."""
        self.HomeAssistant.call_services("media_player", "media_pause", data=self.target)

    def play_pause(self) -> None:
        """Toggle Play/Pause."""
        self.HomeAssistant.call_services("media_player", "media_play_pause", data=self.target)

class Climate(Entity):
    """Representation of a Climate entity."""

    def __init__(self, HomeAssistant: HomeAssistant, entity: dict) -> None:
        super().__init__(HomeAssistant, entity)
        self.hvac_modes = self._entity["attributes"].get("hvac_modes", [])

    def default_action(self):
        self.cycle_mode()

    def cycle_mode(self) -> None:
        """Cycle climate."""
        self.update()
        mode_index = self.hvac_modes.index(self.state) + 1
        if mode_index == len(self.hvac_modes):
            mode_index = 0

        service_data = self.target
        service_data["hvac_mode"] = self.hvac_modes[mode_index]
        self.HomeAssistant.call_services("climate", "set_hvac_mode", data=service_data)

if __name__ == '__main__':
    hass = HomeAssistant(
        "http://10.0.0.12:8123", 
        "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiIxNjlmYTZiNjQwY2Y0MzNlOWEzNjViNDkwNjcxNzEzYyIsImlhdCI6MTYzOTg1MTQ4MywiZXhwIjoxOTU1MjExNDgzfQ.ISu3NP6NesFFX6bcGraG3lNUacxBt6KaPrl2lfeaUYM",
        False
    )
    _ = hass.states()
    for _entity in _:
        if 'climate.dyson_fan' == _entity.entity_id:
            print(_entity.friendly_name)
            _entity.cycle_mode()