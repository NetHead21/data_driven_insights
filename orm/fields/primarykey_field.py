from typing import Any, Dict, Type
from fields.integer_field import IntegerField
from models.model import Model
import uuid


class PrimaryKeyField(IntegerField):
    _auto_id_counters: Dict[Type["Model"], int] = {}

    def __init__(self, auto: bool = False, uuid_mode: bool = False):
        super().__init__()
        self.auto = auto
        self.uuid_mode = uuid_mode

    def __get__(self, instance, owner):
        if instance is None:
            return self

        if not hasattr(instance, self.private_name):
            value = self._generate_id(owner)
            setattr(instance, self.private_name, value)

        return getattr(instance, self.private_name)

    def _generate_id(self, owner) -> Any:
        if self.auto:
            if owner not in PrimaryKeyField._auto_id_counters:
                PrimaryKeyField._auto_id_counters[owner] = 0
            PrimaryKeyField._auto_id_counters[owner] += 1
            return PrimaryKeyField._auto_id_counters[owner]
        elif self.uuid_mode:
            return str(uuid.uuid4())
        return None
