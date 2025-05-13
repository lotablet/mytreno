import json
import os
import voluptuous as vol
from homeassistant import config_entries
from .const import DOMAIN

# Cache stazioni
_STATIONS = None

def get_stations():
  global _STATIONS
  if _STATIONS is None:
    file_path = os.path.join(os.path.dirname(__file__), "stations.json")
    with open(file_path, encoding="utf-8") as f:
      _STATIONS = json.load(f)
  return _STATIONS


class MyTrenoConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
  VERSION = 2

  async def async_step_user(self, user_input=None):
    if user_input is not None:
      mode = user_input["mode"]
      if mode == "stazione":
        return await self.async_step_stazione()
      elif mode == "treno":
        return await self.async_step_treno()

    return self.async_show_form(
      step_id="user",
      data_schema=vol.Schema({
        vol.Required("mode"): vol.In({
          "stazione": "Monitor stazione",
          "treno": "Tracciamento treno"
        })
      })
    )

  async def async_step_stazione(self, user_input=None):
    errors = {}
    stations = get_stations()

    if user_input is not None:
      station_name = user_input.get("station_name")
      station_id = stations.get(station_name)
      if station_id:
        return self.async_create_entry(
          title=station_name,
          data={
            "mode": "stazione",
            "station_id": station_id,
            "station_name": station_name,
          }
        )
      else:
        errors["station_name"] = "invalid_station"

    return self.async_show_form(
      step_id="stazione",
      data_schema=vol.Schema({
        vol.Required("station_name"): vol.In(sorted(stations.keys()))
      }),
      errors=errors
    )

  async def async_step_treno(self, user_input=None):
    errors = {}
    if user_input is not None:
      tn = user_input.get("train_number")
      if tn and tn.isdigit():
        return self.async_create_entry(
          title=f"Treno {tn}",
          data={
            "mode": "treno",
            "train_number": tn,
          }
        )
      else:
        errors["train_number"] = "invalid_train_number"

    return self.async_show_form(
      step_id="treno",
      data_schema=vol.Schema({
        vol.Required("train_number"): str
      }),
      errors=errors
    )
