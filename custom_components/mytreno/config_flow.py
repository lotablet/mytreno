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
  VERSION = 3

  def __init__(self):
    self._filtered_stations: dict = {}
    self._search_query: str = ""

  async def async_step_user(self, user_input=None):
    return self.async_show_menu(
      step_id="user",
      menu_options=["stazione", "treno"],
    )

  async def async_step_stazione(self, user_input=None):
    """Step 1: campo di ricerca testuale."""
    errors = {}

    if user_input is not None:
      query = user_input.get("search", "").strip()
      if len(query) < 2:
        errors["search"] = "query_too_short"
      else:
        stations = get_stations()
        query_lower = query.lower()
        matches = {k: v for k, v in stations.items() if query_lower in k.lower()}
        if not matches:
          errors["search"] = "no_results"
        else:
          self._filtered_stations = matches
          self._search_query = query
          return await self.async_step_stazione_risultati()

    return self.async_show_form(
      step_id="stazione",
      data_schema=vol.Schema({
        vol.Required("search"): str,
      }),
      errors=errors,
      description_placeholders={"hint": "es. Roma, Milano, Napoli…"},
    )

  async def async_step_stazione_risultati(self, user_input=None):
    """Step 2: scelta dalla lista filtrata."""
    errors = {}
    MAX_RESULTS = 30
    options = sorted(self._filtered_stations.keys())[:MAX_RESULTS]
    total = len(self._filtered_stations)

    if user_input is not None:
      station_name = user_input.get("station_name")
      station_id = self._filtered_stations.get(station_name)
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

    hint = (
      f"Trovate {total} stazioni per \"{self._search_query}\" — mostrate le prime {MAX_RESULTS}. "
      "Torna indietro per affinare la ricerca."
      if total > MAX_RESULTS
      else f"Trovate {total} stazioni per \"{self._search_query}\"."
    )

    return self.async_show_form(
      step_id="stazione_risultati",
      data_schema=vol.Schema({
        vol.Required("station_name"): vol.In(options),
      }),
      errors=errors,
      description_placeholders={"hint": hint},
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
