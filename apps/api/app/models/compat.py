"""
Cross-database compatible column types.

Provides UUID, JSONB, and ARRAY types that work with both
PostgreSQL (production) and SQLite (local development).
"""

import json
import uuid as _uuid

from sqlalchemy import String, Text, TypeDecorator, types
from sqlalchemy.dialects import postgresql


class GUID(TypeDecorator):
    """Platform-independent UUID type.
    Uses PostgreSQL's UUID type when available, otherwise stores as CHAR(36).
    """
    impl = String(36)
    cache_ok = True

    def load_dialect_impl(self, dialect):
        if dialect.name == "postgresql":
            return dialect.type_descriptor(postgresql.UUID(as_uuid=True))
        return dialect.type_descriptor(String(36))

    def process_bind_param(self, value, dialect):
        if value is None:
            return value
        if dialect.name == "postgresql":
            return value if isinstance(value, _uuid.UUID) else _uuid.UUID(str(value))
        return str(value) if isinstance(value, _uuid.UUID) else str(_uuid.UUID(str(value)))

    def process_result_value(self, value, dialect):
        if value is None:
            return value
        if isinstance(value, _uuid.UUID):
            return value
        return _uuid.UUID(str(value))


class JSONType(TypeDecorator):
    """Platform-independent JSON type.
    Uses PostgreSQL's JSONB when available, otherwise stores as TEXT with JSON serialization.
    """
    impl = Text
    cache_ok = True

    def load_dialect_impl(self, dialect):
        if dialect.name == "postgresql":
            return dialect.type_descriptor(postgresql.JSONB)
        return dialect.type_descriptor(Text)

    def process_bind_param(self, value, dialect):
        if value is None:
            return value
        if dialect.name == "postgresql":
            return value
        return json.dumps(value, default=str)

    def process_result_value(self, value, dialect):
        if value is None:
            return value
        if isinstance(value, (dict, list)):
            return value
        return json.loads(value)


class ArrayType(TypeDecorator):
    """Platform-independent ARRAY type.
    Uses PostgreSQL's ARRAY when available, otherwise stores as JSON text.
    """
    impl = Text
    cache_ok = True

    def __init__(self, item_type=Text, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._item_type = item_type

    def load_dialect_impl(self, dialect):
        if dialect.name == "postgresql":
            return dialect.type_descriptor(postgresql.ARRAY(self._item_type))
        return dialect.type_descriptor(Text)

    def process_bind_param(self, value, dialect):
        if value is None:
            return value
        if dialect.name == "postgresql":
            return value
        return json.dumps(value, default=str)

    def process_result_value(self, value, dialect):
        if value is None:
            return value
        if isinstance(value, list):
            return value
        return json.loads(value)
