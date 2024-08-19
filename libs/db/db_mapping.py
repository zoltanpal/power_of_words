from sqlalchemy import MetaData
from sqlalchemy.ext.automap import (
    automap_base,
    generate_relationship,
    interfaces,
    name_for_collection_relationship,
)

from libs.db.db_client import SQLDBClient


class SQLDBMapping:
    def __init__(self, db_client: SQLDBClient, mapping_tables: list = None):
        self.metadata = MetaData()
        self.sorted_tables = []
        self.db_client = db_client
        self.mapping_tables = mapping_tables
        self.db_classes = None

        self.mapping()

    def mapping(self):
        if not self.db_client:
            return False

        if self.mapping_tables:
            self.metadata.reflect(
                self.db_client.engine, only=self.mapping_tables, views=True
            )
        else:
            self.metadata.reflect(self.db_client.engine, views=True)

        AutoBase = automap_base(metadata=self.metadata)
        AutoBase.prepare(
            name_for_collection_relationship=self._name_for_collection_relationship,
            generate_relationship=self._generate_relationship,
        )

        self.sorted_tables = [table.name for table in self.metadata.sorted_tables]
        self.db_classes = AutoBase.classes

    def __getattr__(self, item: str):
        if item not in self.db_classes:
            raise KeyError(f"'{item}' table not found or not mapped.")

    def __getitem__(self, item: str):
        if item not in self.db_classes:
            raise KeyError(f"'{item}' table not found or not mapped.")

    def get(self, item: str):
        if item not in self.db_classes:
            raise AttributeError(f"'{item}' table not found or not mapped.")
        return getattr(self.db_classes, item)

    @property
    def mapped_table_names(self):
        return (
            [x.__table__ for x in list(self.db_classes.db_classes)]
            if self.db_classes
            else []
        )

    @staticmethod
    def _generate_relationship(
        base, direction, return_fn, attr_name, local_cls, referred_cls, **kw
    ):
        if direction is interfaces.ONETOMANY:
            kw["cascade"] = "all, delete"
            kw["passive_deletes"] = False

        return generate_relationship(
            base, direction, return_fn, attr_name, local_cls, referred_cls, **kw
        )

    @staticmethod
    def _name_for_collection_relationship(base, local_cls, referred_cls, constraint):
        if constraint.name:
            return constraint.name.lower()

        return name_for_collection_relationship(
            base, local_cls, referred_cls, constraint
        )
