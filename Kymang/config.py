import os

from dotenv import load_dotenv

load_dotenv(".env")


BOT_TOKEN = os.environ.get("BOT_TOKEN", "")
API_ID = int(os.environ.get("API_ID", ""))
API_HASH = os.environ.get("API_HASH", "")
MONGO_URL = os.environ.get("MONGO_URL", "")
ADMINS = [int(x) for x in (os.environ.get("ADMINS", "").split())]
MEMBER = [int(x) for x in (os.environ.get("MEMBER", "160").split())]
LOG_GRP = int(os.environ.get("LOG_GRP", ""))
BOT_ID = int(os.environ.get("BOT_ID", ""))

OWNER_ID = int(os.environ.get("OWNER_ID", 1760633466))
ADMINS.append(OWNER_ID)

ewallet_nomor = os.environ.get("WALLET_NO")
bca_nomor = os.environ.get("BCA_NO")
qris = os.environ.get("QRIS")
ewallet_name = os.environ.get("WALLET_NAME")
bca_name = os.environ.get("BCA_NAME")
qris_name = os.environ.get("QRIS_NAME")
payment_nomor = {"bca": bca_nomor, "e-wallet": ewallet_nomor, "qris": qris}
payment_name = {"bca": bca_name, "e-wallet": ewallet_name, "qris": qris_name}
