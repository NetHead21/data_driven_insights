import datetime
import json
import os
import uuid
from typing import Any, Dict, List, Optional, Type


class Field:
    def __init__(self, required: bool = False, default: Optional[Any] = None):
        self.required = required
        self.default = default

    def __set_name__(self, owner, name):
        self.private_name = "_" + name

    def __get__(self, instance, owner):
        return getattr(instance, self.private_name, None)

    def __set__(self, instance, value):
        setattr(instance, self.private_name, value)


class StringField(Field):
    def __set__(self, instance, value):
        if not isinstance(value, str):
            raise TypeError("Expected a string")
        super().__set__(instance, value)


class IntegerField(Field):
    def __set__(self, instance, value):
        if not isinstance(value, int):
            raise TypeError("Expected an integer")
        super().__set__(instance, value)


class AutoTimestampField(StringField):
    def __get__(self, instance, owner):
        if not hasattr(instance, self.private_name):
            now = datetime.datetime.now().isoformat()
            setattr(instance, self.private_name, now)
        return getattr(instance, self.private_name)


class Model:
    _fields_cache: Dict[Type["Model"], Dict[str, Field]] = {}

    def __init__(self, **kwargs):
        fields = self._get_fields()

        # Validate required fields
        missing_fields = [
            field_name
            for field_name, field in fields.items()
            if field.required and field_name not in kwargs and field.default is None
        ]
        if missing_fields:
            raise ValueError(
                f"Missing required fields {missing_fields} in {self.__class__.__name__}"
            )

        # Set default values for fields
        for field_name, field in fields.items():
            if field_name not in kwargs and field.default is not None:
                setattr(self, field_name, field.default)

        # Set provided values and validate
        invalid_fields = [key for key in kwargs if key not in fields]
        if invalid_fields:
            raise AttributeError(
                f"Invalid fields {invalid_fields} for class '{self.__class__.__name__}'"
            )

        for key, value in kwargs.items():
            setattr(self, key, value)

    @classmethod
    def get_table_name(cls) -> str:
        if hasattr(cls, "Meta") and hasattr(cls.Meta, "table_name"):
            return cls.Meta.table_name
        return f"{cls.__name__}.json"

    @classmethod
    def _get_fields(cls) -> Dict[str, Field]:
        if cls not in Model._fields_cache:
            Model._fields_cache[cls] = {
                key: field
                for key, field in cls.__dict__.items()
                if isinstance(field, Field)
            }
        return Model._fields_cache[cls]

    def to_dict(self) -> Dict[str, Any]:
        return {key: getattr(self, key) for key in self._get_fields()}

    def save(self):
        if hasattr(self, "before_save"):
            self.before_save()

        if hasattr(self, "clean"):
            self.clean()

        file_name = self.get_table_name()

        # Load existing data
        if os.path.exists(file_name):
            try:
                with open(file_name, "r") as file:
                    data = json.load(file)
            except json.JSONDecodeError:
                data = []
        else:
            data = []

        # Check for existing record and update
        record = self.to_dict()
        for i, item in enumerate(data):
            if item.get("uid") == record.get("uid"):
                data[i] = record
                break
        else:
            data.append(record)

        # Save updated data
        with open(file_name, "w") as file:
            json.dump(data, file, indent=2)

    @classmethod
    def all(cls) -> List["Model"]:
        file_name = cls.get_table_name()
        if not os.path.exists(file_name):
            return []

        try:
            with open(file_name, "r") as file:
                raw_data = json.load(file)
        except (json.JSONDecodeError, FileNotFoundError):
            return []

        return [
            cls(**item)
            for item in raw_data
            if isinstance(item, dict) and cls._is_valid_entry(item)
        ]

    @classmethod
    def _is_valid_entry(cls, item: Dict[str, Any]) -> bool:
        try:
            cls(**item)
            return True
        except (TypeError, ValueError):
            return False

    @classmethod
    def filter(cls, **kwargs) -> List["Model"]:
        return [
            obj
            for obj in cls.all()
            if all(getattr(obj, key) == value for key, value in kwargs.items())
        ]

    @classmethod
    def get(cls, **kwargs) -> "Model":
        matches = cls.filter(**kwargs)
        if not matches:
            raise ValueError(f"No {cls.__name__} found with {kwargs}")

        if len(matches) > 1:
            raise ValueError(f"Multiple {cls.__name__} instances match {kwargs}")
        return matches[0]


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


class User(Model):
    uid = PrimaryKeyField(auto=True)
    name = StringField(required=True)
    age = IntegerField()

    def clean(self) -> None:
        if self.age is not None and self.age < 18:
            raise ValueError("Age must be at least 18")

    def before_save(self) -> None:
        self.name = self.name.title()

    class Meta:
        table_name = "users_data.json"


if __name__ == "__main__":
    user1 = User(name="John Doe", age=30)
    user1.save()
    user2 = User(name="Jane Doe", age=25)
    user2.save()
    user3 = User(name="Juniven", age=30)
    user3.save()

    # user4 = User(name="Charlie", age=15)
    # user4.save()  # This will raise a ValueError

    users = User.all()
    for user in users:
        print(f"{user.name} is {user.age} years old")

    # test error
    # user2 = User(age=12)

    users = User.filter(name="John Doe")
    for user in users:
        print(f"Found user: {user.name} is {user.age} years old")

    # test error
    # user = User.get(name="Charlie")
