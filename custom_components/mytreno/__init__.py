import voluptuous as vol
from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers import config_validation as cv

from .const import DOMAIN, SERVICE_SET_TRAIN

PLATFORMS = ["sensor"]

SET_TRAIN_SCHEMA = vol.Schema({
    vol.Required("train_number"): cv.string,
    vol.Optional("entry_id"): cv.string,
})

async def async_setup(hass: HomeAssistant, _: dict) -> bool:
    """Serve solo a far esistere il dominio prima delle ConfigEntry."""
    hass.data.setdefault(DOMAIN, {})
    return True

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Setup della singola config entry."""
    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN].setdefault(entry.entry_id, {})

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    if not hass.services.has_service(DOMAIN, SERVICE_SET_TRAIN):

        async def _handle_set_train(call: ServiceCall) -> None:
            tn = call.data["train_number"]
            entry_id = call.data.get("entry_id")

            targets = (
                [hass.data[DOMAIN].get(entry_id)]
                if entry_id
                else [hass.data[DOMAIN].get("global_tracking")]
            )

            for tgt in targets:
                if not tgt:
                    continue
                container = tgt.get("train_container")
                coordinator = tgt.get("train_coordinator")
                if container is not None:
                    container["train_number"] = tn
                    if coordinator:
                        await coordinator.async_request_refresh()

        hass.services.async_register(
            DOMAIN,
            SERVICE_SET_TRAIN,
            _handle_set_train,
            schema=SET_TRAIN_SCHEMA
        )

    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unloads a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)

    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id, None)

    return unload_ok

async def async_reload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Reloads a config entry."""
    await async_unload_entry(hass, entry)
    return await async_setup_entry(hass, entry)
