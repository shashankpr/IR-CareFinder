from os import environ
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())

settings = {
    "foursquare": {
        "client_id": environ.get("FOURSQUARE_CLIENT_ID"),
        "client_secret": environ.get("FOURSQUARE_CLIENT_SECRET"),
    }
}