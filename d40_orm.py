import json
import os


class Field:
    def __init__(self, required=False):
        self.required = required

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


class Model:
    _fields_cache = None

    def __init__(self, **kwargs):
        fields = self._get_fields()
        for field_name, field in fields.items():
            if field.required and field_name not in kwargs:
                raise ValueError(f"Missing required field: {field_name}")
        for key, value in kwargs.items():
            if key not in self._get_fields():
                raise AttributeError(f"Unknown field: {key}")
            # Use the descriptor logic to validate and set the value
            setattr(self, key, value)

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
        file_name = self._get_file_name()

        data = []
        if os.path.exists(file_name):
            with open(file_name, "r") as file:
                try:
                    data = json.load(file)
                except json.JSONDecodeError:
                    pass

        data.append(self.to_dict())
        with open(file_name, "w") as file:
            json.dump(data, file, indent=2)

    @classmethod
    def all(cls):
        file_name = f"{cls.__name__}.json"
        if not os.path.exists(file_name):
            return []

        with open(file_name, "r") as file:
            try:
                raw_data = json.load(file)
                return [cls(**item) for item in raw_data]
            except json.JSONDecodeError:
                return []

    @classmethod
    def filter(cls, **kwargs):
        results = []
        for obj in cls.all():
            match = True

            for key, value in kwargs.items():
                if getattr(obj, key) != value:
                    match = False
                    break
            if match:
                results.append(obj)
        return results

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

            instance._id = random.randint(1000, 9999)
        return instance._id


class User(Model):
    name = StringField(required=True)
    age = IntegerField()


if __name__ == "__main__":
    User(name="John Doe", age=30).save()
    User(name="Jane Doe", age=25).save()
    User(name="Juniven", age=30).save()

    users = User.all()
    for user in users:
        print(f"{user.name} is {user.age} years old")

    # test error
    # user2 = User(age=12)
