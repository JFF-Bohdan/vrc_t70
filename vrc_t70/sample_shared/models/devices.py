import datetime

from .shared import Base, types_holder


class VrcT70Device(Base):
    __tablename__ = "vrc_t70_devices"

    __table_args__ = (
        types_holder.UniqueConstraint("device_address", name="unq1_vrc_t70_devices_device_address"),
    )

    device_id = types_holder.Column(types_holder.Integer, primary_key=True)
    device_address = types_holder.Column(types_holder.SmallInteger, nullable=False)
    device_name = types_holder.Column(types_holder.String(255), nullable=True)

    adding_timestamp = types_holder.Column(types_holder.DateTime, nullable=False, default=datetime.datetime.utcnow)

    last_update_timestamp = types_holder.Column(
        types_holder.DateTime,
        nullable=False,
        default=datetime.datetime.utcnow,
        onupdate=datetime.datetime.utcnow
    )
