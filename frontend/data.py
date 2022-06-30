import pandas as pd
import typing
import os
import base64
import datetime
import numpy as np
from dateutil.parser import parse
from sqlalchemy import select
from .database import legacy_engine
from .models import Vehicle, Record, LastRecord

import pandas as pd

API_END_POINT = "https://ds4a-api.muniter.xyz"
CACHE = "/tmp/ds4a_cache"


# vectorized haversine function
def haversine(lat1, lon1, lat2, lon2, to_radians=True, earth_radius=6371):
    """
    slightly modified version: of http://stackoverflow.com/a/29546836/2901002

    Calculate the great circle distance between two points
    on the earth (specified in decimal degrees or in radians)

    All (lat, lon) coordinates must have numeric dtypes and be of equal length.

    """
    if to_radians:
        lat1 = np.radians(lat1)
        lon1 = np.radians(lon1)
        lat2 = np.radians(lat2)
        lon2 = np.radians(lon2)

    a = (
        np.sin((lat2 - lat1) / 2.0) ** 2
        + np.cos(lat1) * np.cos(lat2) * np.sin((lon2 - lon1) / 2.0) ** 2
    )

    return earth_radius * 2 * np.arcsin(np.sqrt(a))


def calculate_distance(data: pd.DataFrame) -> pd.DataFrame:
    if "distance" not in data.columns:
        data["distance"] = haversine(
            data.latitude.shift(1),
            data.longitude.shift(1),
            data.loc[1:, "latitude"],
            data.loc[1:, "longitude"],
        )
        data["cum_distance"] = data.distance.cumsum()

    return data


def calculate_speed(data: pd.DataFrame) -> pd.DataFrame:
    if "distance" not in data.columns:
        if "speed" not in data.columns:
            # Calculate the speed from the distance and the datetime difference
            data["speed"] = data.distance / (
                data.datetime.diff() / np.timedelta64(1, "s")
            )

    return data


def compute(data: pd.DataFrame) -> pd.DataFrame:
    """
    Compute the data.
    """
    data = calculate_distance(data)
    data = calculate_speed(data)
    return data


def get_data(id: str, sql) -> pd.DataFrame:
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


def get_vehicle_data(
    vehicle_name: str,
    start_date: str | datetime.datetime,
    end_date: str | datetime.datetime,
) -> pd.DataFrame:
    """
    Get data for a specific vehicle.
    """
    # convert str to datetime then to format YYYY-MM-DDTHH:MM:SS
    if type(start_date) is str:
        start_date = parse(start_date)
    if type(end_date) is str:
        end_date = parse(end_date)
    sql = (
        select(Record)
        .where(
            Record.vehicle_id
            == select(Vehicle.id).where(Vehicle.name == vehicle_name).limit(1)
        )
        .where(Record.datetime >= start_date)
        .where(Record.datetime <= end_date)
        .order_by(Record.datetime)
    )
    data = get_data("".join([vehicle_name, str(start_date), str(end_date)]), sql)
    if not data.empty:
        data = compute(data)
    return data


def last_record() -> pd.DataFrame:
    """
    Get the last record.
    """
    sql = select(LastRecord)
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
    },
}
