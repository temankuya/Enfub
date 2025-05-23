import logging
import time
from os import execvp
from sys import executable


class ConnectionHandler(logging.Handler):
    def __init__(self):
        super().__init__()
        self.last_restart = 0  

    def emit(self, record):
        if record.exc_info and isinstance(record.exc_info[1], OSError):
            now = time.time()
            if now - self.last_restart > 10:  
                LOGS.warning("OSError terdeteksi! Me-restart bot...")
                self.last_restart = now
                execvp(executable, [executable, "-m", "Kymang"])
            else:
                LOGS.warning("Restart dicegah: terlalu cepat setelah restart terakhir.")


logger = logging.getLogger()
logger.setLevel(logging.INFO)

formatter = logging.Formatter("[%(levelname)s] - %(name)s - %(message)s", "%d-%b %H:%M")
stream_handler = logging.StreamHandler()
stream_handler.setFormatter(formatter)

logger.addHandler(stream_handler)
logger.addHandler(ConnectionHandler())

logging.getLogger("pyrogram").setLevel(logging.ERROR)
logging.getLogger("pyrogram.client").setLevel(logging.ERROR)
logging.getLogger("pyrogram.session.auth").setLevel(logging.CRITICAL)
logging.getLogger("pyrogram.session.session").setLevel(logging.CRITICAL)


LOGS = logging.getLogger(__name__)


def LOGGER(name: str) -> logging.Logger:
    
    logger = logging.getLogger(name)
    if not logger.handlers: 
        formatter = logging.Formatter("[%(levelname)s] - %(name)s - %(message)s", "%d-%b %H:%M")
        handler = logging.StreamHandler()
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
    return logger
