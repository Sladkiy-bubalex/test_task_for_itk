import os
import logging
from redis.asyncio import Redis as AsyncRedis
from passlib.context import CryptContext
from logging.handlers import RotatingFileHandler
from dotenv import load_dotenv


load_dotenv()


logger = logging.getLogger()
logger.setLevel(logging.INFO)
handler = RotatingFileHandler("app.log", maxBytes=20000, backupCount=2)
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
logger.addHandler(handler)
logger.addHandler(console_handler)

pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")

async_redis_client = AsyncRedis(host="redis", port=6379, db=0)

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRE_HOURS = int(os.getenv("ACCESS_TOKEN_EXPIRE_HOURS"))
