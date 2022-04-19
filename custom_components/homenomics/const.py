import logging

DOMAIN = "homenomics"

CONF_API_KEY = "api_key"
CONF_CRYPTOCURRENCIES = "cryptocurrencies"
CONF_LOCAL_CURRENCY = "local_currency"
CONF_UPDATE_FREQUENCY = "update_frequency"

SENSOR_PREFIX = "HomeNomics "
ATTR_MARKET_CAP = "market_cap"
ATTR_SYMBOL = "symbol"
ATTR_LOGO_URL = "logo_url"
ATTR_RANK = "rank"
ATTR_HIGH = "high"
ATTR_HIGH_TIMESTAMP = "high_timestamp"
ATTR_1_HR = "1_hr"
ATTR_24_HR = "24_hr"
ATTR_7_DAY = "7_day"
ATTR_30_DAY = "30_day"
ATTR_1_HR_PCT = "1_hr_pct"
ATTR_24_HR_PCT = "24_hr_pct"
ATTR_7_DAY_PCT = "7_day_pct"
ATTR_30_DAY_PCT = "30_day_pct"
ATTR_LAST_UPDATE = "last_update"

API_ENDPOINT = "https://api.nomics.com/v1/"

_LOGGER = logging.getLogger(__name__)
