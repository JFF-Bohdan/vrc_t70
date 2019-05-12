import datetime

from .shared import Base, SqliteNumeric, types_holder


class VrcT70Sensor(Base):
    """"""
    __tablename__ = "vrc_t70_sensors"

    __table_args__ = (
        types_holder.Index("idx1_vrc_t70_sensors_device_id", "device_id"),
        types_holder.Index("idx2_vrc_t70_sensors_device_id_sensor_address", "device_id", "sensor_address"),
        types_holder.UniqueConstraint("sensor_address", name="unq1_sensor_address"),
    )

    sensor_id = types_holder.Column(types_holder.Integer, primary_key=True)

    sensor_address = types_holder.Column(types_holder.String(64), nullable=False, unique=True)

    device_id = types_holder.Column(
        types_holder.Integer,
        types_holder.ForeignKey("vrc_t70_devices.device_id"),
        nullable=False
    )

    trunk_number = types_holder.Column(types_holder.Integer, nullable=False)
    sensor_index = types_holder.Column(types_holder.Integer, nullable=False)

    temperature = types_holder.Column(SqliteNumeric, nullable=False)

    is_connected = types_holder.Column(types_holder.Boolean, nullable=False, default=False)

    adding_timestamp = types_holder.Column(types_holder.DateTime, nullable=False, default=datetime.datetime.utcnow)

    last_update_timestamp = types_holder.Column(
        types_holder.DateTime,
        nullable=False,
        default=datetime.datetime.utcnow,
        onupdate=datetime.datetime.utcnow
    )
