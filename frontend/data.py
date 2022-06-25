import pandas as pd
import typing
import json
import requests
import os
import base64
import datetime
from dateutil.parser import parse

import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import urllib.parse

API_END_POINT = "https://ds4a-api.muniter.xyz"
CACHE = "/tmp/ds4a_cache"


def get_data(url: str) -> pd.DataFrame:
    """
    Get data from the API or Cache.
    """
    # Encode the URL to base64
    url_encoded = base64.b64encode(url.encode("utf-8")).decode("utf-8")
    if not os.path.exists("/tmp/ds4a_cache_" + url_encoded):
        # If the file does not exist, get it from the API
        response = requests.get(url)
        if response.status_code == 200:
            # If the request was successful, save it to the cache
            with open("/tmp/ds4a_cache_" + url_encoded, "w") as f:
                f.write(response.text)

            return pd.DataFrame(response.json())
        else:
            raise Exception("Error: " + str(response.status_code) + " " + response.text + " " + url)
    else:
        with open("/tmp/ds4a_cache_" + url_encoded, "r") as f:
            return typing.cast(pd.DataFrame, pd.read_json(f))


def get_vehicle_data(vehicle_name: str, start_date: str, end_date: str) -> pd.DataFrame:
    """
    Get data for a specific vehicle.
    """
    # convert str to datetime then to format YYYY-MM-DDTHH:MM:SS
    start = parse(start_date).strftime("%Y-%m-%dT%H:%M:%S")
    end = parse(end_date).strftime("%Y-%m-%dT%H:%M:%S")
    return get_data(f"{API_END_POINT}/record/{vehicle_name}/{start}/{end}")

last_records = get_data(API_END_POINT + "/last_record")
last_records.datetime = pd.to_datetime(last_records.datetime)
vehicles = get_data(API_END_POINT + "/vehicle")
general = {
    "median_location": {
        "latitude": last_records["latitude"].median(),
        "longitude": last_records["longitude"].median(),
    },
    "date_range": {
        "start": datetime.datetime(2021, 4, 1),
        "end": datetime.datetime(2021, 4, 2),
    }
}
