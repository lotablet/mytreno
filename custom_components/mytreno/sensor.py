from __future__ import annotations

from datetime import timedelta
import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import (
    DataUpdateCoordinator,
    CoordinatorEntity,
)
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.entity import generate_entity_id

from .const  import DOMAIN
from .utils  import fetch_data, fetch_train_data

_LOGGER = logging.getLogger(__name__)
ENTITY_ID_FORMAT = "sensor.mytreno_{}"
GLOBAL_TRACK_KEY = "global_tracking"          # sensore unico “selected train”

# ─────────────────────────────────────────────────────────────────────────────
#  Entity: Tabellone stazione
# ─────────────────────────────────────────────────────────────────────────────
class MyTrenoStationSensor(CoordinatorEntity):
    _attr_icon = "mdi:train"

    def __init__(self, coordinator, station_id, station_name):
        super().__init__(coordinator)
        slug = station_name.lower().replace(" ", "_")
        self.entity_id = generate_entity_id(
            ENTITY_ID_FORMAT, slug, hass=coordinator.hass
        )
        self._attr_unique_id = f"{DOMAIN}_station_{slug}"
        self._attr_name = station_name
        self._attr_device_info = {
            "identifiers": {(DOMAIN, station_id)},
            "name": f"Stazione {station_name}",
            "manufacturer": "Trenitalia",
            "model": "MyTreno Station",
            "entry_type": "service",
        }

    @property
    def state(self):
        return "ok"           # heartbeat

    @property
    def extra_state_attributes(self):
        return self.coordinator.data


# ─────────────────────────────────────────────────────────────────────────────
#  Entity: Treno selezionato (globale)
# ─────────────────────────────────────────────────────────────────────────────
class MyTrenoSelectedTrainSensor(CoordinatorEntity):
    _attr_icon = "mdi:train-car"

    def __init__(self, coordinator, container):
        super().__init__(coordinator)
        self._container = container
        self.entity_id       = "sensor.mytreno_selected_train"
        self._attr_unique_id = f"{DOMAIN}_selected_train"
        self._attr_name      = "Treno selezionato"
        self._attr_device_info = None           # sensore slegato da device

    @property
    def state(self):
        return self.coordinator.data.get("ritardo")

    @property
    def extra_state_attributes(self):
        return self.coordinator.data


# ─────────────────────────────────────────────────────────────────────────────
#  Setup entry: crea sensori e coordinator
# ─────────────────────────────────────────────────────────────────────────────
async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    station_id   = entry.data["station_id"]
    station_name = entry.title

    # ------ tabellone stazione ------
    async def _upd_station():
        return await fetch_data(hass, station_id)

    station_coord = DataUpdateCoordinator(
        hass,
        logger=_LOGGER,
        name=f"mytreno_station_{station_id}",
        update_method=_upd_station,
        update_interval=timedelta(minutes=5),
    )
    await station_coord.async_config_entry_first_refresh()

    async_add_entities(
        [MyTrenoStationSensor(station_coord, station_id, station_name)], True
    )

    # ------ sensore globale “selected train” ------
    if GLOBAL_TRACK_KEY not in hass.data.setdefault(DOMAIN, {}):
        container = {"train_number": None}

        async def _upd_train():
            tn = container["train_number"]
            return await fetch_train_data(hass, tn) if tn else {}

        track_coord = DataUpdateCoordinator(
            hass,
            logger=_LOGGER,
            name="mytreno_selected_train_global",
            update_method=_upd_train,
            update_interval=timedelta(seconds=30),
        )
        await track_coord.async_refresh()

        async_add_entities(
            [MyTrenoSelectedTrainSensor(track_coord, container)], True
        )

        # riferimenti globali (usati dal service set_train)
        hass.data[DOMAIN][GLOBAL_TRACK_KEY] = {
            "train_container":   container,
            "train_coordinator": track_coord,
        }
