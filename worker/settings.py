from os import environ
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())

settings = {
    "foursquare": {
        "client_id": environ.get("FOURSQUARE_CLIENT_ID"),
        "client_secret": environ.get("FOURSQUARE_CLIENT_SECRET"),
    },

    "redis": {
        "host": environ.get("REDIS_HOST", 'localhost'),
        "port": environ.get("REDIS_PORT", '6379'),
        "auth": environ.get("REDIS_AUTH", ''),
    },

    "mysql": {
        "host": environ.get("MYSQL_HOST", 'localhost'),
        "user": environ.get("MYSQL_USER", 'ir'),
        "pass": environ.get("MYSQL_PASS", 'ir'),
        "db": environ.get("MYSQL_DB", 'information-retrieval'),
    }
}
