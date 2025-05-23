import os

from dotenv import load_dotenv

load_dotenv(".env")


BOT_TOKEN = os.environ.get("BOT_TOKEN", "8108394845:AAF0YFsdZEZCDHBW-v4R5EIuea-1DcTwqxo")
API_ID = int(os.environ.get("API_ID", "21140864"))
API_HASH = os.environ.get("API_HASH", "9dbae6c11aa0a1c06da19d52deada7b9")
MONGO_URL = os.environ.get("MONGO_URL", "mongodb+srv://Moshi:<db_password>@cluster0.fnu5ste.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")
ADMINS = [int(x) for x in (os.environ.get("ADMINS", "1371054078").split())]
MEMBER = [int(x) for x in (os.environ.get("MEMBER", "160").split())]
LOG_GRP = int(os.environ.get("LOG_GRP", "-1002639054633"))
BOT_ID = int(os.environ.get("BOT_ID", "8108394845"))

OWNER_ID = int(os.environ.get("OWNER_ID", 1371054078))
ADMINS.append(OWNER_ID)

ewallet_nomor = os.environ.get("WALLET_NO")
bca_nomor = os.environ.get("BCA_NO")
qris = os.environ.get("QRIS")
ewallet_name = os.environ.get("WALLET_NAME")
bca_name = os.environ.get("BCA_NAME")
qris_name = os.environ.get("QRIS_NAME")
payment_nomor = {"bca": bca_nomor, "e-wallet": ewallet_nomor, "qris": qris}
payment_name = {"bca": bca_name, "e-wallet": ewallet_name, "qris": qris_name}
