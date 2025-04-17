
from .const import DOMAIN

PLATFORMS = ["sensor"]

async def async_setup_entry(hass, config_entry):
    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][config_entry.entry_id] = config_entry.data

    await hass.config_entries.async_forward_entry_setups(config_entry, PLATFORMS)
    return True
