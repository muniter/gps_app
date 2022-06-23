from .database import Base
from sqlalchemy import Column, String, Text, BigInteger, Float, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship


class Vehicle(Base):
    """
    Stores the vehicle information.
    """
    __tablename__ = "vehicle"

    def __repr__(self):
        return "<Vehicle(id={}, {})>".format(self.id, self.name)

    id = Column(BigInteger, primary_key=True)
    name = Column(String(100), nullable=False)

class Record(Base):
    """
    Stores the record information.
    """
    __tablename__ = "record"

    def __repr__(self):
        return "<Record(id={}, vehicle_id={}, datetime={})>".format(
            self.id, self.vehicle_id, self.datetime
        )

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    altitude = Column(Float, nullable=True)
    speed = Column(Float, nullable=True)
    datetime = Column(DateTime, index=True, nullable=False)
    direction = Column(Float, nullable=True)
    vehicle_id = Column(BigInteger, ForeignKey("vehicle.id"), index=True, nullable=False)
    vehicle = relationship("Vehicle")
    event = Column(Text, nullable=True)
    ignition = Column(Boolean, nullable=True)
    battery = Column(Float, nullable=True)
    backup_battery = Column(Float, nullable=True)

class LastRecord(Base):
    """
    Stores the last records of each vehicle.

    Acts as a sort of cache, for initial requests from the client/front end.
    """
    __tablename__ = "last_record"

    def __repr__(self):
        return "<LastRecord(id={}, vehicle_id={}, datetime={})>".format(
            self.id, self.vehicle_id, self.datetime
        )

    vehicle_name = Column(String(100), nullable=False)
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    altitude = Column(Float, nullable=True)
    speed = Column(Float, nullable=True)
    datetime = Column(DateTime, index=True, nullable=False)
    direction = Column(Float, nullable=True)
    vehicle_id = Column(BigInteger, ForeignKey("vehicle.id"), index=True, nullable=False)
    vehicle = relationship("Vehicle")
    event = Column(Text, nullable=True)
    ignition = Column(Boolean, nullable=True)
    battery = Column(Float, nullable=True)
    backup_battery = Column(Float, nullable=True)
