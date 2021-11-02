"""Luxtronik heatpump number."""
# region Imports
import logging
import time
from threading import Timer
from typing import Any, Final, Literal

from homeassistant.components.number import NumberEntity
from homeassistant.components.sensor import (ENTITY_ID_FORMAT,
                                             STATE_CLASS_MEASUREMENT,
                                             SensorEntity)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (CONF_SENSORS, DEVICE_CLASS_TEMPERATURE,
                                 DEVICE_CLASS_TIMESTAMP, PRECISION_HALVES,
                                 PRECISION_TENTHS, TEMP_CELSIUS, TIME_SECONDS)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import DeviceInfo, async_generate_entity_id
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import ConfigType, StateType
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from . import LuxtronikDevice
from .const import *

# from homeassistant.components.number.const import MODE_AUTO, MODE_BOX, MODE_SLIDER


# endregion Imports

# region Constants
# endregion Constants

async def async_setup_platform(
    hass: HomeAssistant, config: ConfigType, async_add_entities: AddEntitiesCallback, discovery_info: dict[str, Any] = None,
) -> None:
    luxtronik: LuxtronikDevice = hass.data.get(DOMAIN)
    if not luxtronik:
        LOGGER.warning("number.async_setup_platform no luxtronik!")
        return False

    deviceInfo = hass.data[f"{DOMAIN}_DeviceInfo"]
    deviceInfoDomesticWater = hass.data[f"{DOMAIN}_DeviceInfo_Domestic_Water"]
    deviceInfoHeating = hass.data[f"{DOMAIN}_DeviceInfo_Heating"]
    entities = [
        LuxtronikNumber(hass, luxtronik, deviceInfoHeating, LUX_SENSOR_HEATING_TEMPERATURE_CORRECTION,
                        'heating_temperature_correction', 'Temperature Correction', False,
                        'mdi:plus-minus-variant', DEVICE_CLASS_TEMPERATURE, STATE_CLASS_MEASUREMENT,
                        TEMP_CELSIUS, -5.0, 5.0, 0.5),

        LuxtronikNumber(hass, luxtronik, deviceInfoDomesticWater, LUX_SENSOR_DOMESTIC_WATER_TARGET_TEMPERATURE,
                        'domestic_water_target_temperature', 'Domestic Water Target Temperature', False,
                        'mdi:water-boiler', DEVICE_CLASS_TEMPERATURE, STATE_CLASS_MEASUREMENT,
                        TEMP_CELSIUS, 40.0, 60.0, 2.5),
    ]
    deviceInfoCooling = hass.data[f"{DOMAIN}_DeviceInfo_Cooling"]

    async_add_entities(entities)


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Set up a Luxtronik number from ConfigEntry."""
    await async_setup_platform(hass, {}, async_add_entities)


class LuxtronikNumber(NumberEntity):
    """Representation of a Luxtronik number."""
    # _attr_should_poll = True

    def __init__(
        self,
        hass: HomeAssistant,
        luxtronik: LuxtronikDevice,
        deviceInfo: DeviceInfo,
        number_key: str,
        unique_id: str,
        name: str,
        assumed: bool,
        icon: str = 'mdi:thermometer',
        device_class: str = DEVICE_CLASS_TEMPERATURE,
        state_class: str = STATE_CLASS_MEASUREMENT,
        unit_of_measurement: str = TEMP_CELSIUS,

        min_value: float = None,  # | None = None,
        max_value: float = None,  # | None = None,
        step: float = None,  # | None = None,
        mode: Literal["auto", "box", "slider"] = "auto",  # MODE_AUTO,
    ) -> None:
        """Initialize the number."""
        self._hass = hass
        self._luxtronik = luxtronik
        self._number_key = number_key

        self.entity_id = ENTITY_ID_FORMAT.format(f"{DOMAIN}_{unique_id}")
        self._attr_unique_id = self.entity_id
        self._attr_device_class = device_class
        self._attr_name = name
        self._attr_assumed_state = assumed
        self._icon = icon
        # self._attr_icon = icon
        self._attr_native_unit_of_measurement = unit_of_measurement
        self._attr_state_class = state_class

        self._attr_device_info = deviceInfo
        self._attr_mode = mode

        if min_value is not None:
            self._attr_min_value = min_value
        if max_value is not None:
            self._attr_max_value = max_value
        if step is not None:
            self._attr_step = step

    @property
    def icon(self):  # -> str | None:
        """Return the icon to be used for this entity."""
        # if type(self._icon) is dict and not isinstance(self._icon, str):
        #     return self._icon[self.native_value()]
        return self._icon

    # @property
    # def native_value(self):  # -> float | int | None:
    #     """Return the state of the number."""
    #     return self._luxtronik.get_value(self._number_key)

    def update(self):
        """Get the latest status and use it to update our sensor state."""
        self._luxtronik.update()

    @property
    def value(self) -> float:
        """Return the state of the entity."""
        return self._luxtronik.get_value(self._number_key)

    async def async_set_value(self, value: float) -> None:
        """Update the current value."""
        self._luxtronik.write(self._number_key.split('.')[1], value)

    # @callback
    # def _update_and_write_state(self, *_):
    #     """Update the number and write state."""
    #     self._update()
    #     self.async_write_ha_state()
