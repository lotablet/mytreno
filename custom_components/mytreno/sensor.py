
import aiohttp
import logging
from datetime import datetime, timezone, timedelta
from homeassistant.helpers.update_coordinator import (
    CoordinatorEntity,
    DataUpdateCoordinator,
    UpdateFailed,
)
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.config_entries import ConfigEntry
from .const import DOMAIN, URL_BASE

_LOGGER = logging.getLogger(__name__)

def build_timestamp():
    now = datetime.now(timezone(timedelta(hours=2)))
    return now.strftime('%a %b %d %Y %H:%M:%S GMT+0200 (Ora legale dell’Europa centrale)')

async def fetch_data(hass: HomeAssistant, station_id: str):
    timestamp = build_timestamp()
    urls = {
        "partenze": f"{URL_BASE}/partenze/{station_id}/{timestamp}",
        "arrivi": f"{URL_BASE}/arrivi/{station_id}/{timestamp}",
    }
    data = {"partenze": [], "arrivi": []}
    session = async_get_clientsession(hass)

    for tipo, url in urls.items():
        try:
            async with session.get(url, timeout=10) as res:
                if res.status != 200:
                    continue
                treni_raw = await res.json()
                if not isinstance(treni_raw, list):
                    continue
                for treno in treni_raw[:10]:
                    data[tipo].append({
                        "treno": treno.get("compNumeroTreno", "??"),
                        "orario": treno.get("compOrarioPartenza" if tipo == "partenze" else "compOrarioArrivo", "??"),
                        "destinazione" if tipo == "partenze" else "provenienza": treno.get("destinazione" if tipo == "partenze" else "origine", "??"),
                        "ritardo": treno.get("ritardo", "?")
                    })
        except Exception as e:
            raise UpdateFailed(f"Errore fetch {tipo}: {e}")
    return data

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback):
    station_id = entry.data["station_id"]
    name = f"MyTreno {station_id}"

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
    async_add_entities([MyTrenoSensor(coordinator, station_id, name)], True)

class MyTrenoSensor(CoordinatorEntity):
    def __init__(self, coordinator, station_id, name):
        super().__init__(coordinator)
        self._station_id = station_id
        self._attr_name = name
        self._attr_unique_id = f"mytreno_{station_id.lower()}"
        self._attr_device_info = {
            "identifiers": {(DOMAIN, station_id)},
            "name": f"Stazione {station_id}",
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
