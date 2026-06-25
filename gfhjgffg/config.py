import os

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

BOT_TOKEN = (
    os.getenv("BOT_TOKEN")
    or os.getenv("TELEGRAM_BOT_TOKEN")
    or os.getenv("TOKEN")
)

ADMINS = [7145919720, 2017236812]
ADMIN_ID = 7145919720

TGRASS_API_KEY = os.getenv("TGRASS_API_KEY", "c9550fc62e794e6daef377ac4286cc06")
BOTOHUB_API_KEY = os.getenv("BOTOHUB_API_KEY", "71edb002-d556-43a8-ab58-e184a5f707b5")
