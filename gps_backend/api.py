from . import app, session
from sqlalchemy import select
from .models import Vehicle, Record, LastRecord
from .schemas import vehicle_schema, record_schema, record_query_schema, last_record_schema
from marshmallow import ValidationError
# from flask import jsonify
import typing

def _get_vehicles(name: str|None = None):
    if isinstance(name, str):
        return typing.cast(Vehicle, session.execute(select(Vehicle).where(Vehicle.name == name)).scalar_one_or_none())
    else:
        return typing.cast(list[Vehicle], session.execute(select(Vehicle)).scalars().all())

@app.route('/', methods=['GET'])
def alive():
    # Test if the database is alive
    try:
        session.execute(select(Vehicle).limit(1))
        return "OK"
    except Exception as e:
        return str(e)

@app.route('/vehicle', methods=['GET'])
def get_vehicles():
    """
    Returns a list of all vehicles.
    """
    vehicles = _get_vehicles()
    return vehicle_schema.dumps(vehicles, many=True)

@app.route('/vehicle/<string:name>', methods=['GET'])
def get_vehicle(name):
    """
    Get a vehicle by name.
    """
    vehicle = _get_vehicles(name)
    if vehicle:
        return vehicle_schema.dumps(vehicle)
    else:
        return 'Vehicle not found', 404


@app.route('/record/<string:name>/<string:start>/<string:end>', methods=['GET'])
def get_record(name, start, end):
    """
    Get records for a vehicle between two dates.
    """
    try:
        query = typing.cast(dict, record_query_schema.load({'vehicle_name': name, 'start': start, 'end': end}))
        # SELECT * FROM record WHERE vehicle_id = (SELECT id FROM vehicle WHERE name = 'WEJ996' LIMIT 1) AND datetime >= '2021-04-12' AND datetime <= '2021-06-13';
        records = session.execute(select(Record).where(Record.vehicle_id == select(Vehicle.id).where(Vehicle.name == query['vehicle_name']).limit(1)).where(Record.datetime >= query['start']).where(Record.datetime <= query['end'])).scalars().all()
        return record_schema.dumps(records, many=True)
    except ValidationError as e:
        return str(e.messages), 400


@app.route('/last_record', methods=['GET'])
def get_last_records():
    """
    Get the last record for all vehicles.
    """
    records = session.execute(select(LastRecord)).scalars().all()
    return last_record_schema.dumps(records, many=True)
