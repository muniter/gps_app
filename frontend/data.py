import pandas as pd
import typing
import json
import requests
import os
import base64
import datetime
from dateutil.parser import parse
from sqlalchemy import select
from .database import session_factory, legacy_engine
from .models import Vehicle, Record, LastRecord

import pandas as pd

API_END_POINT = "https://ds4a-api.muniter.xyz"
CACHE = "/tmp/ds4a_cache"
session = session_factory()

def get_data(id:str, sql) -> pd.DataFrame:
    """
    Get data from the API or Cache.
    """
    # Encode the URL to base64
    identifier = base64.b64encode(id.encode("utf-8")).decode("utf-8")
    if not os.path.exists("/tmp/ds4a_cache_" + identifier):
        # If the file does not exist, get it from the API
        data = pd.read_sql(sql, legacy_engine)
        if not data.empty and type(data) is pd.DataFrame:
            data.to_json("/tmp/ds4a_cache_" + identifier, orient="records")
        return data
    else:
        with open("/tmp/ds4a_cache_" + identifier, "r") as f:
            return typing.cast(pd.DataFrame, pd.read_json(f))


def get_vehicle_data(vehicle_name: str, start_date: str, end_date: str) -> pd.DataFrame:
    """
    Get data for a specific vehicle.
    """
    # convert str to datetime then to format YYYY-MM-DDTHH:MM:SS
    start = parse(start_date).strftime("%Y-%m-%dT%H:%M:%S")
    end = parse(end_date).strftime("%Y-%m-%dT%H:%M:%S")
    sql = (select(Record).where(Record.vehicle_id == select(Vehicle.id).where(Vehicle.name == vehicle_name).limit(1)).where(Record.datetime >= start).where(Record.datetime <= end))
    return get_data("".join([vehicle_name, start, end]), sql)

def last_record() -> pd.DataFrame:
    """
    Get the last record.
    """
    sql = (select(LastRecord))
    return pd.read_sql(sql, legacy_engine)

last_records = get_data("last_records", select(LastRecord))
vehicles = get_data("vehicles", select(Vehicle))
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
