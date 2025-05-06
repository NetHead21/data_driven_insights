import datetime
import json
import os
import uuid


class Field:
    def __init__(self, required=False, default=None):
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
            setattr(instance, self.private_name, datetime.datetime.now().isoformat())
        if not hasattr(instance, self.private_name):
            now = datetime.datetime.now().isoformat()
            self.__set__(instance, now)


class Model:
    _fields_cache = None

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
    def get_table_name(cls):
        if hasattr(cls, "Meta") and hasattr(cls.Meta, "table_name"):
            return cls.Meta.table_name
        return f"{cls.__name__}.json"

    @classmethod
    def _get_fields(cls):
        if cls._fields_cache is None:
            cls._fields_cache = {
                key: field
                for key, field in cls.__dict__.items()
                if isinstance(field, Field)
            }
        return cls._fields_cache

    def to_dict(self):
        return {key: getattr(self, key) for key in self._get_fields()}

    def _get_file_name(self):
        return f"{self.__class__.__name__}.json"

    def save(self):
        file_name = self.get_table_name()

        if os.path.exists(file_name):
            try:
                with open(file_name, "r") as file:
                    data = json.load(file)
            except json.JSONDecodeError:
                data = []
        else:
            data = []

        data.append(self.to_dict())
        with open(file_name, "w") as file:
            json.dump(data, file, indent=2)

    @classmethod
    def all(cls):
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
    def _is_valid_entry(cls, item):
        try:
            cls(**item)
            return True
        except (TypeError, ValueError):
            return False

    @classmethod
    def filter(cls, **kwargs):
        return [
            obj
            for obj in cls.all()
            if all(getattr(obj, key) == value for key, value in kwargs.items())
        ]

    @classmethod
    def get(cls, **kwargs):
        matches = cls.filter(**kwargs)
        if not matches:
            raise ValueError("No {cls.__name__} found with {kwargs}")

        if len(matches) > 1:
            raise ValueError("Multiple {cls.__name__} instance match {kwargs}")
        return matches[0]


class IDField(IntegerField):
    def __set__(self, intance, value):
        raise AttributeError("ID is read-only")

    def __get__(self, instance, owner):
        if not hasattr(instance, "_id"):
            import random

            instance._id = random.randint(999, 9999)
        return instance._id


class PrimaryKeyField(IntegerField):
    _auto_id = 0

    def __init__(self, auto=False, uuid_mode=False):
        super().__init__()
        self.auto = auto
        self.uuid_mode = uuid_mode

    def __get__(self, instance, _):
        if instance is None:
            return self

        if not hasattr(instance, self.private_name):
            value = self._generate_id()
            setattr(instance, self.private_name, value)

        return getattr(instance, self.private_name, None)

    def _generate_id(self):
        if self.auto:
            PrimaryKeyField._auto_id += 1
            return PrimaryKeyField._auto_id
        elif self.uuid_mode:
            return str(uuid.uuid4())
        return None


class User(Model):
    uid = PrimaryKeyField(auto=True)
    name = StringField(required=True)
    age = IntegerField()

    class Meta:
        table_name = "users_data.json"


if __name__ == "__main__":
    user1 = User(name="John Doe", age=30)
    user1.save()
    user2 = User(name="Jane Doe", age=25)
    user2.save()
    user3 = User(name="Juniven", age=30)
    user3.save()

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
