from decimal import Decimal as D

import sqlalchemy.types as types
import sqlalchemy as types_holder  # noqa
from sqlalchemy.ext.declarative import declarative_base


class SqliteNumeric(types.TypeDecorator):
    impl = types.String

    def load_dialect_impl(self, dialect):
        return dialect.type_descriptor(types.VARCHAR(100))

    def process_bind_param(self, value, dialect):
        return str(value)

    def process_result_value(self, value, dialect):
        return D(value)


Base = declarative_base()
