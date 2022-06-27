"""Platform for light integration."""
from __future__ import annotations

import logging

import voluptuous as vol

# Import the device class from the component that you want to support
import homeassistant.helpers.config_validation as cv
from homeassistant.components.light import (ATTR_BRIGHTNESS, PLATFORM_SCHEMA,
                                            LightEntity, ColorMode)
from homeassistant.const import CONF_HOST, CONF_PASSWORD, CONF_USERNAME
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import ConfigType, DiscoveryInfoType

import requests

_LOGGER = logging.getLogger(__name__)

# Validation of the user's configuration
PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    vol.Required(CONF_HOST): cv.string,
    # vol.Optional(CONF_USERNAME, default='admin'): cv.string,
    # vol.Optional(CONF_PASSWORD): cv.string,
})


def setup_platform(
    hass: HomeAssistant,
    config: ConfigType,
    add_entities: AddEntitiesCallback,
    discovery_info: DiscoveryInfoType | None = None
) -> None:
    """Set up the Awesome Light platform."""
    # Assign configuration variables.
    # The configuration check takes care they are present.
    host = config[CONF_HOST]
    # username = config[CONF_USERNAME]
    # password = config.get(CONF_PASSWORD)

    # Setup connection with devices/cloud
      #hub = awesomelights.Hub(host, username, password)
    hub=Ilamp_api(host)

    # Verify that passed in configuration works
    if not hub.connect():
        _LOGGER.error("Could not connect to iLamp API")
        return

    # Add devices
    add_entities(Ilamp(hub))

class Ilamp_api:
    def __init__(self, host):
        self.url=requests.get("http://"+host+":8585/").url
        
        self._brightness=255
        self._color=(255,255,255)
        self._white=1
        self._state=True
        self._mode="white"

        def req(self, action, arguments=""):
            requests.get(self.url+"/api/lamp/?action="+action+"&"+arguments)
        
        def color2hex(self):
            return '%02x%02x%02x' % self._color

        @property
        def state(self):
            return self._state
        @state.setter
        def state(self, state):
            if state:
                if self._mode=="white":
                    self.req("poweron_white")
                else:
                    self.req("poweron_color")
            else:
                self.req("poweroff")

        @property
        def brightness(self):
            return self._brightness
        @brightness.setter
        def brightness(self, brightness):
            brightness=brightness/255
            self.req("brightness", "color="+self.color2hex())

class Ilamp(LightEntity):
    """Representation of an iLamp Light."""

    def __init__(self, light) -> None:
        """Initialize an AwesomeLight."""
        self._light = light
        self._name = light.name
        self._state = True

        self._brightness = 1.0
        self._color_temp = 1.0

        self._color_mode = ColorMode.COLOR_TEMP
        self._rgb_color=(0,0,0)

        self._supported_color_modes = set([ColorMode.COLOR_TEMP, ColorMode.RGB])

    @property
    def name(self) -> str:
        """Return the display name of this light."""
        return self._name

    @property
    def brightness(self):
        """Return the brightness of the light.

        This method is optional. Removing it indicates to Home Assistant
        that brightness is not supported for this light.
        """
        return self._brightness
    
    @property
    def color_temp(self):
        """Return the CT color value in mireds.

        This method is optional. Removing it indicates to Home Assistant
        that brightness is not supported for this light.
        """
        return self._color_temp

    @property
    def color_mode(self):
        """Return the color mode of the light.

        This method is optional. Removing it indicates to Home Assistant
        that brightness is not supported for this light.
        """
        return self._color_mode
    
    @property
    def rgb_color(self):
        return self._rgb_color

    @property
    def is_on(self) -> bool | None:
        """Return true if light is on."""
        return self._state

    def turn_on(self, **kwargs: Any) -> None:
        """Instruct the light to turn on.

        You can skip the brightness part if your light does not support
        brightness control.
        """
        self._light.brightness = kwargs.get(ATTR_BRIGHTNESS, 255)
        self._light.state=True

    def turn_off(self, **kwargs: Any) -> None:
        """Instruct the light to turn off."""
        self._light.turn_off()

    def update(self) -> None:
        """Fetch new state data for this light.

        This is the only method that should fetch new data for Home Assistant.
        """
        self._light.update()
        self._state = self._light.state
        self._brightness = self._light.brightness*255
