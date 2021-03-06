"""
Sensor component for HomeNomics
Author: McCookieM
"""
import requests
import voluptuous as vol
from datetime import datetime, date, timedelta
import urllib.error
from typing import Any, Callable, Dict, Optional

from homeassistant.components.sensor import PLATFORM_SCHEMA, SensorDeviceClass
import homeassistant.helpers.config_validation as cv
from homeassistant.util import Throttle
from homeassistant.helpers.entity import Entity
from homeassistant.helpers.typing import (
    HomeAssistantType,
    ConfigType,
    DiscoveryInfoType,
)

from .const import (
    _LOGGER,
    DOMAIN,
    SENSOR_PREFIX,
    API_ENDPOINT,
    CONF_API_KEY,
    CONF_CRYPTOCURRENCIES,
    CONF_LOCAL_CURRENCY,
    CONF_UPDATE_FREQUENCY,
    ATTR_MARKET_CAP,
    ATTR_SYMBOL,
    ATTR_CURRENCY,
    ATTR_LOGO_URL,
    ATTR_RANK,
    ATTR_HIGH,
    ATTR_HIGH_TIMESTAMP,
    ATTR_1_HR,
    ATTR_24_HR,
    ATTR_7_DAY,
    ATTR_30_DAY,
    ATTR_1_HR_PCT,
    ATTR_24_HR_PCT,
    ATTR_7_DAY_PCT,
    ATTR_30_DAY_PCT,
    ATTR_LAST_UPDATE,
)

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend(
    {
        vol.Required(CONF_API_KEY): cv.string,
        vol.Required(CONF_CRYPTOCURRENCIES): cv.ensure_list,
        vol.Optional(CONF_LOCAL_CURRENCY, default="usd"): cv.string,
        vol.Optional(CONF_UPDATE_FREQUENCY, default=60): cv.string,
    }
)

SCAN_INTERVAL = timedelta(minutes=1)

def setup_platform(
    hass: HomeAssistantType,
    config: ConfigType,
    add_entities: Callable,
    discovery_info: Optional[DiscoveryInfoType]=None,
) -> None:
    """Set up the sensor platform."""
    _LOGGER.debug("Setting up HomeNomics sensor platform")

    api_key = config[CONF_API_KEY]
    cryptos = config[CONF_CRYPTOCURRENCIES]
    local_currency = config[CONF_LOCAL_CURRENCY]
    throttle = timedelta(minutes=(int(config[CONF_UPDATE_FREQUENCY])))
    
    hndata = NomicsData(
        api_key,
        cryptos,
        local_currency,
        throttle
    )
    
    hndata.update()

    sensors = [
        HomeNomicsSensor(
            crypto,
            hndata
        )
        for crypto in cryptos
    ]

    add_entities(sensors, update_before_add=True)
    
    return True
        
class HomeNomicsSensor(Entity):
    """Representation of a HomeNomics crypto sensor."""
    
    def __init__(self, crypto:str, hndata):
        super().__init__()
        self.data = None
        self.hndata = hndata
        self.crypto = crypto.upper().strip()
        self.local_currency = hndata.GetLocalCurrency()
        self._attr_device_class = SensorDeviceClass.MONETARY
        self._name = (SENSOR_PREFIX + self.crypto + " " + self.local_currency)
        self._icon = "mdi:circle-multiple"
        self._state = None
        self._available = True
        self._last_update = None
        self._market_cap = None
        self._symbol = None
        self._currency = None
        self._logo_url = None
        self._rank = None
        self._high = None
        self._high_timestamp = None
        self._1_hr = None
        self._24_hr = None
        self._7_day = None
        self._30_day = None
        self._1_hr_pct = None
        self._24_hr_pct = None
        self._7_day_pct = None
        self._30_day_pct = None
        self._unit_of_measurement = self.local_currency

    @property
    def name(self) -> str:
        return self._name

    @property
    def icon(self) -> str:
        return self._icon

    @property
    def state(self) -> Optional[str]:
        return self._state

    @property
    def unique_id(self) -> str:
        return f"{DOMAIN}-{self.crypto}-{self.local_currency}"
    
    @property
    def unit_of_measurement(self) -> str:
        return self._unit_of_measurement
    
    @property
    def available(self) -> bool:
        return self._available

    @property
    def extra_state_attributes(self):
        return {
            ATTR_LAST_UPDATE: self._last_update,
            ATTR_MARKET_CAP: self._market_cap,
            ATTR_SYMBOL: self._symbol,
            ATTR_CURRENCY: self._currency,
            ATTR_LOGO_URL: self._logo_url,
            ATTR_RANK: self._rank,
            ATTR_HIGH: self._high,
            ATTR_HIGH_TIMESTAMP: self._high_timestamp,
            ATTR_1_HR: self._1_hr,
            ATTR_24_HR: self._24_hr,
            ATTR_7_DAY: self._7_day,
            ATTR_30_DAY: self._30_day,
            ATTR_1_HR_PCT: self._1_hr_pct,
            ATTR_24_HR_PCT: self._24_hr_pct,
            ATTR_7_DAY_PCT: self._7_day_pct,
            ATTR_30_DAY_PCT: self._30_day_pct
        }
    
    def update(self):
        try:
            self.hndata.update()
            coinData = self.hndata.GetData(self.crypto)
            lastUpdate = self.hndata.GetLastUpdate()
            
            if coinData:
                # Set the values of the sensor
                self._last_update = lastUpdate
                # set the attributes of the sensor
                self._market_cap = coinData["market_cap"]
                self._symbol = coinData["symbol"]
                self._currency = coinData["currency"]
                self._logo_url = coinData["logo_url"]
                self._rank = coinData["rank"]
                self._high = coinData["high"]
                self._high_timestamp = coinData["high_timestamp"]
                self._1_hr = coinData["1_hr"]
                self._1_hr_pct = coinData["1_hr_pct"]
                self._24_hr = coinData["24_hr"]
                self._24_hr_pct = coinData["24_hr_pct"]
                self._7_day = coinData["7_day"]
                self._7_day_pct = coinData["7_day_pct"]
                self._30_day = coinData["30_day"]
                self._30_day_pct = coinData["30_day_pct"]
                
                # Set state and availability
                self._state = coinData["current_price"]
                self._available = True
            else:
                raise ValueError()
        except ValueError:
            self._state = None
            self._last_update = datetime.today().strftime("%d-%m-%Y %H:%M")
            self._market_cap = None
            self._symbol = None
            self._currency = None
            self._logo_url = None
            self._rank = None
            self._high = None
            self._high_timestamp = None
            self._high_timestamp = datetime(1970,1,1).strftime("%d-%m-%Y %H:%M")
            self._1_hr = None
            self._24_hr = None
            self._7_day = None
            self._30_day = None
            self._1_hr_pct = None
            self._24_hr_pct = None
            self._7_day_pct = None
            self._30_day_pct = None
            self._available = False
        except Exception as err:
            self._available = False
            _LOGGER.exception(f"Error setting values using data from Nomics API - {err=}")

class NomicsData:
    def __init__(self, api_key, cryptos, local_currency, throttle):
        self._api_key = api_key
        self._cryptos = []
        for crypto in cryptos:
            self._cryptos.append(crypto.upper().strip())
        self._local_currency = local_currency.upper().strip()
        self._last_update = ""
        self._nomicsdata = {}
        self.update = Throttle(throttle)(self._update)

    def GetLastUpdate(self) -> str:
        return self._last_update
    
    def GetLocalCurrency(self) -> str:
        return self._local_currency
    
    def GetData(self, crypto):
        if crypto in self._nomicsdata:
            return self._nomicsdata[crypto]

    def _update(self):
        try:
            url = (
                API_ENDPOINT
                + "currencies/ticker?key=" + self._api_key
                + "&ids=" + ','.join(self._cryptos)
                + "&interval=1h,1d,7d,30d"
                + "&convert=" + self._local_currency
            )
            
            # sending get request
            r = requests.get(url=url)
            
            # extracting response json            
            objData = {}
            for obj in r.json():
                # Tidy up and add required data
                entry = {}
                entry["id"] = obj["id"]
                entry["currency"] = obj["name"]
                entry["current_price"] = float(obj["price"]) if "price" in obj else None
                entry["symbol"] = obj["symbol"] if "symbol" in obj else None
                entry["logo_url"] = obj["logo_url"] if "logo_url" in obj else None
                entry["market_cap"] = obj["market_cap"] if "market_cap" in obj else None
                if "high" in obj:
                    entry["high"] = float(obj["high"])
                    high_dt = datetime.strptime(obj["high_timestamp"],"%Y-%m-%dT%H:%M:%SZ")
                    entry["high_timestamp"] = high_dt.strftime("%d-%m-%Y %H:%M")
                else:
                    entry["high"] = None
                    entry["high_timestamp"] = None
                entry["rank"] = obj["rank"] if "rank" in obj else None
                if "1h" in obj:
                    entry["1_hr"] = float(obj["1h"]["price_change"])
                    entry["1_hr_pct"] = round(float(obj["1h"]["price_change_pct"]) * 100, 4)
                else:
                    entry["1_hr"] = None
                    entry["1_hr_pct"] = None
                if "1d" in obj:
                    entry["24_hr"] = float(obj["1d"]["price_change"])
                    entry["24_hr_pct"] = round(float(obj["1d"]["price_change_pct"]) * 100, 4)
                else:
                    entry["24_hr"] = None
                    entry["24_hr_pct"] = None
                if "7d" in obj:
                    entry["7_day"] = float(obj["7d"]["price_change"])
                    entry["7_day_pct"] = round(float(obj["7d"]["price_change_pct"]) * 100, 4)
                else:
                    entry["7_day"] = None
                    entry["7_day_pct"] = None
                if "30d" in obj:
                    entry["30_day"] = float(obj["30d"]["price_change"])
                    entry["30_day_pct"] = round(float(obj["30d"]["price_change_pct"]) * 100, 4)
                else:
                    entry["30_day"] = None
                    entry["30_day_pct"] = None
                
                objData[obj["id"]] = entry
            
            self._nomicsdata = objData
            self._last_update = datetime.now().strftime("%d-%m-%Y %H:%M")

        except Exception as err:
            _LOGGER.exception(f"Error retrieving data from Nomics API - {err=}")
