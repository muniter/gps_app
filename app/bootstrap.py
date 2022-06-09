from .database import engine
from .models import *
from datetime import datetime as dt
from pathlib import Path
from sqlalchemy import select
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.session import Session
from typing import Dict

import csv
import json
import os
import os.path as path
import typing

# data is a folder with CSV files, each csv files is the data of a vehicle for
# a month. The name of the vehicle can be retrieved by splitting the file name
# by the '-' character and taking the second part
DATA_DIR = "data"
PROCESSED_FILE = "processed"

# TODO:
# Skip empty sheets

FIELD_MAP: Dict[str, tuple[str, bool]] = {
    "latitude": ("Latitude", True),
    "longitude": ("Longitude", True),
    "altitude": ("Altitud", False),
    "speed": ("Speed", True),
    "datetime": ("Date time", True),
    "direction": ("Curso", False),
    "vehicle_id": ("ID", True),
    "vehicle": ("", False),
    "event": ("Event", False),
    "ignition": ("Ignicion", False),
    "battery": ("Batería Vehiculo", False),
    "backup_battery": ("Batería Respaldo", False),
}


def file_check(csvfile) -> bool:
    try:
        return csv.Sniffer().has_header(csvfile.read(1024))
    except:
        print("Skipping file, does not have header")
        return False


def get_vehicle(filename: Path, db: Session) -> Vehicle:
    with open(filename, "r") as csvfile:
        for row in csv.DictReader(csvfile):
            vehicle_id = row["ID"]
            try:
                vehicle_id = int(vehicle_id)
            except ValueError:
                raise ValueError("No vehicle ID found in the data")

            vehicle = db.execute(
                select(Vehicle).where(Vehicle.id == vehicle_id)
            ).scalar_one_or_none()
            if vehicle is None:
                # Add it to the session
                vehicle = Vehicle(
                    name=filename.stem.split("-", maxsplit=1)[1],
                    id=vehicle_id,
                )
                db.add(vehicle)
                return vehicle
            else:
                return typing.cast(Vehicle, vehicle)

        raise ValueError("Vehicle ID not found")


def record_from_previous(row, previous) -> Record:
    """Event rows sometimes don't have multiple required fields, like latitude and longitude.
    Workaround by getting the last valid record, and replacing the event value.
    """
    values = previous.__dict__.copy()
    values.pop("_sa_instance_state", None)  # sqlalchemy state
    values["event"] = row.get(FIELD_MAP["event"][0])
    r = Record(**values)
    return r


def record_from_row(row: dict, records: list[Record], vehicle: Vehicle) -> Record:
    values = {}
    is_event = row.get(FIELD_MAP["event"][0]) is not None
    for k, v in FIELD_MAP.items():
        orig_k, required = v
        val = row.get(orig_k)
        if required and not val:
            if is_event:
                if any(records):
                    return record_from_previous(row, records[-1])
                else:
                    raise ValueError(
                        (
                            "Skipping row, is an event but there's no previous record to use for the missing values"
                        )
                    )
            else:
                raise ValueError(
                    ("Skipping row, no required field: {}".format(orig_k))
                )

        values[k] = val if val != "" else None

    if values["ignition"] is not None:
        values["ignition"] = bool(values["ignition"])

    # Should always work since datetime is a required field
    values["datetime"] = dt.strptime(values["datetime"], "%Y-%m-%d %H:%M:%S")
    values["vehicle"] = vehicle

    return Record(**values)


def record_builder(file: Path, db: Session) -> bool:
    with open(file, "r") as csvfile:
        # TODO: Implement
        if not file_check(csvfile):
            return False

        try:
            vehicle = get_vehicle(file, db)
        except ValueError:
            print("Vehicle not found skipping file {}".format(file))
            return False

        records: list[Record] = []
        counter = 0
        csvfile.seek(0)
        reader = csv.DictReader(csvfile)
        for row in reader:

            try:
                r = record_from_row(row, records, vehicle)
                records.append(r)
            except Exception as e:
                print(f"Skipping row #{counter} got error {e.args}")

        try:
            db.add_all(records)
            db.commit()
            return True
        except Exception as e:
            print("Failed adding data from file {}".format(file))
            print("Got error {}".format(e))
            db.rollback()
            raise e

def append_to_processed(name):
    with open(PROCESSED_FILE, 'a') as file:
        file.write(str(name) + "\n")

def load_processed():
    processed = {}
    with open(PROCESSED_FILE, 'r') as file:
        for line in file:
            processed[line.strip()] = True
    return processed


def run():
    db: Session = sessionmaker(bind=engine, autocommit=False, autoflush=False)()
    # Iterate recursively over all files in the data folder
    processed = load_processed()
    counter = len(processed)
    for root, _, files in os.walk(DATA_DIR):
        for file in files:
            file = Path(root) / file
            if file.suffix == ".csv" and str(file) not in processed:
                counter += 1
                print(f"Processing file #{counter}: {file}")
                record_builder(file, db)
                append_to_processed(file)
