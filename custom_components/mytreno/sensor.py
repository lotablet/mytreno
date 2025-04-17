
from datetime import timedelta
import logging

from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, CoordinatorEntity
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.entity import generate_entity_id

from .const import DOMAIN, URL_BASE
from .utils import fetch_data

_LOGGER = logging.getLogger(__name__)
ENTITY_ID_FORMAT = "sensor.mytreno_{}"

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback):
    station_id = entry.data["station_id"]
    station_name = entry.title  # friendly_name leggibile

    async def async_update_data():
        return await fetch_data(hass, station_id)

    coordinator = DataUpdateCoordinator(
        hass,
        logger=_LOGGER,
        name="mytreno",
        update_method=async_update_data,
        update_interval=timedelta(minutes=5),
    )

    await coordinator.async_config_entry_first_refresh()
    async_add_entities([MyTrenoSensor(coordinator, station_id, station_name)], True)

class MyTrenoSensor(CoordinatorEntity):
    def __init__(self, coordinator, station_id, station_name):
        super().__init__(coordinator)
        self._station_id = station_id
        self._attr_name = station_name

        slug = station_name.lower().replace(" ", "_")
        self.entity_id = generate_entity_id(ENTITY_ID_FORMAT, slug, hass=coordinator.hass)

        self._attr_unique_id = f"mytreno_{slug}"
        self._attr_device_info = {
            "identifiers": {(DOMAIN, station_id)},
            "name": f"Stazione {station_name}",
            "manufacturer": "Trenitalia",
            "model": "MyTreno Sensor",
            "entry_type": "service"
        }

    @property
    def state(self):
        return "ok"

    @property
    def extra_state_attributes(self):
        return self.coordinator.data
