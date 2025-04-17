import aiohttp
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import UpdateFailed
from datetime import datetime, timezone, timedelta

from .const import URL_BASE

def build_timestamp():
    now = datetime.now(timezone(timedelta(hours=2)))
    return now.strftime('%a %b %d %Y %H:%M:%S GMT+0200 (Ora legale dell’Europa centrale)')

# Funzione per convertire numeri romani in numeri arabi
def roman_to_int(roman):
    roman_numerals = {
        "I": 1, "II": 2, "III": 3, "IV": 4, "V": 5, "VI": 6, "VII": 7,
        "VIII": 8, "IX": 9, "X": 10, "XI": 11, "XII": 12, "XIII": 13,
        "XIV": 14, "XV": 15, "XVI": 16, "XVII": 17, "XVIII": 18, "XIX": 19,
        "XX": 20
    }
    return roman_numerals.get(roman, roman)  # Restituisce il numero o la stringa originale se non trovato

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
                        "ritardo": treno.get("ritardo", "?"),
                        "binario_previsto": roman_to_int(treno.get("binarioProgrammatoPartenzaDescrizione", "N/A")),  # binario previsto
                        "binario_effettivo": roman_to_int(treno.get("binarioEffettivoPartenzaDescrizione", "N/A"))  # binario effettivo
                    })
        except Exception as e:
            raise UpdateFailed(f"Errore fetch {tipo}: {e}")
    return data
