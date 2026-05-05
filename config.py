import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN", "")
PAYMENT_TOKEN = os.getenv("PAYMENT_TOKEN", "")

# Default to Moscow for fallback natal chart values.
DEFAULT_TZ_OFFSET = os.getenv("DEFAULT_TZ_OFFSET", "+03:00")
DEFAULT_LAT = os.getenv("DEFAULT_LAT", "55.7558")
DEFAULT_LON = os.getenv("DEFAULT_LON", "37.6176")
