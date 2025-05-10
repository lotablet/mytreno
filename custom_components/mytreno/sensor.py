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

from .const import DOMAIN
from .utils import fetch_data, fetch_train_data

_LOGGER = logging.getLogger(__name__)
ENTITY_ID_FORMAT = "sensor.mytreno_{}"
GLOBAL_TRACK_KEY = "global_tracking"  # sensore unico “selected train”


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
        return "ok"  # heartbeat

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
        self.entity_id = "sensor.mytreno_selected_train"
        self._attr_unique_id = f"{DOMAIN}_selected_train"
        self._attr_name = "Treno selezionato"
        self._attr_device_info = None

    @property
    def state(self):
        return self.coordinator.data.get("ritardo")

    @property
    def extra_state_attributes(self):
        return self.coordinator.data


# ─────────────────────────────────────────────────────────────────────────────
#  Entity: Treno fisso configurato
# ─────────────────────────────────────────────────────────────────────────────
class MyTrenoStaticTrainSensor(CoordinatorEntity):
    _attr_icon = "mdi:train-car"

    def __init__(self, coordinator, train_number):
        super().__init__(coordinator)
        self.entity_id = f"sensor.mytreno_treno_{train_number}"
        self._attr_unique_id = f"{DOMAIN}_static_{train_number}"
        self._attr_name = f"Treno {train_number}"
        self._train_number = train_number
        self._attr_device_info = {
            "identifiers": {(DOMAIN, train_number)},
            "name": f"Treno {train_number}",
            "manufacturer": "Trenitalia",
            "model": "MyTreno Static Train",
            "entry_type": "service",
        }

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

    # --- STAZIONE ---
    station_id = entry.data.get("station_id")
    station_name = entry.title

    if station_id:
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

    # --- TRENO SELEZIONATO GLOBALE (una sola volta) ---
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

        hass.data[DOMAIN][GLOBAL_TRACK_KEY] = {
            "train_container": container,
            "train_coordinator": track_coord,
        }

    # --- TRENO FISSO CONFIGURATO ---
    train_number = entry.data.get("train_number")
    if train_number:
        async def _upd_static():
            return await fetch_train_data(hass, train_number)

        static_coord = DataUpdateCoordinator(
            hass,
            logger=_LOGGER,
            name=f"mytreno_static_train_{train_number}",
            update_method=_upd_static,
            update_interval=timedelta(seconds=60),
        )
        await static_coord.async_config_entry_first_refresh()

        async_add_entities(
            [MyTrenoStaticTrainSensor(static_coord, train_number)], True
        )
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

from .const import DOMAIN
from .utils import fetch_data, fetch_train_data

_LOGGER = logging.getLogger(__name__)
ENTITY_ID_FORMAT = "sensor.mytreno_{}"
GLOBAL_TRACK_KEY = "global_tracking"  # sensore unico “selected train”


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
        return "ok"  # heartbeat

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
        self.entity_id = "sensor.mytreno_selected_train"
        self._attr_unique_id = f"{DOMAIN}_selected_train"
        self._attr_name = "Treno selezionato"
        self._attr_device_info = None

    @property
    def state(self):
        return self.coordinator.data.get("ritardo")

    @property
    def extra_state_attributes(self):
        return self.coordinator.data


# ─────────────────────────────────────────────────────────────────────────────
#  Entity: Treno fisso configurato
# ─────────────────────────────────────────────────────────────────────────────
class MyTrenoStaticTrainSensor(CoordinatorEntity):
    _attr_icon = "mdi:train-car"

    def __init__(self, coordinator, train_number):
        super().__init__(coordinator)
        self.entity_id = f"sensor.mytreno_treno_{train_number}"
        self._attr_unique_id = f"{DOMAIN}_static_{train_number}"
        self._attr_name = f"Treno {train_number}"
        self._train_number = train_number
        self._attr_device_info = {
            "identifiers": {(DOMAIN, train_number)},
            "name": f"Treno {train_number}",
            "manufacturer": "Trenitalia",
            "model": "MyTreno Static Train",
            "entry_type": "service",
        }

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

    # --- STAZIONE ---
    station_id = entry.data.get("station_id")
    station_name = entry.title

    if station_id:
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

    # --- TRENO SELEZIONATO GLOBALE (una sola volta) ---
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

        hass.data[DOMAIN][GLOBAL_TRACK_KEY] = {
            "train_container": container,
            "train_coordinator": track_coord,
        }

    # --- TRENO FISSO CONFIGURATO ---
    train_number = entry.data.get("train_number")
    if train_number:
        async def _upd_static():
            return await fetch_train_data(hass, train_number)

        static_coord = DataUpdateCoordinator(
            hass,
            logger=_LOGGER,
            name=f"mytreno_static_train_{train_number}",
            update_method=_upd_static,
            update_interval=timedelta(seconds=60),
        )
        await static_coord.async_config_entry_first_refresh()

        async_add_entities(
            [MyTrenoStaticTrainSensor(static_coord, train_number)], True
        )
