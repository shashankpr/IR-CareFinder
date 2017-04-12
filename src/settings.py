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
        "password": environ.get("REDIS_PASSWORD", ''),
    },

    "mysql": {
        "host": environ.get("MYSQL_HOST", 'localhost'),
        "user": environ.get("MYSQL_USER", 'ir'),
        "pass": environ.get("MYSQL_PASS", 'ir'),
        "db": environ.get("MYSQL_DB", 'information-retrieval'),
    },

    "elastic": {
        "host": environ.get("ELASTIC_HOST", 'localhost'),
        "port": environ.get("ELASTIC_PORT", '9200'),
        "user": environ.get("ELASTIC_USER", ''),
        "pass": environ.get("ELASTIC_PASS", ''),
    },

    "knowledge_graph": {
        "key": environ.get("GKG_APIKEY"),
    },

    "webdav": {
        'webdav_hostname': environ.get("WEBDAV_HOSTNAME"),
        'webdav_root': environ.get("WEBDAV_ROOT"),
        'webdav_login': environ.get("WEBDAV_LOGIN"),
        'webdav_password': environ.get("WEBDAV_PASSWORD"),
    },

    "warc": {
        'path': environ.get("WARC_STORAGE")
    }

}

# Setting for `rq worker`

REDIS_HOST = settings['redis']['host']
REDIS_PORT = settings['redis']['port']
REDIS_PASSWORD = settings['redis']['password']
