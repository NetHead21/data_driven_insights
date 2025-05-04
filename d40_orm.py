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


class User(Model):
    name = StringField(required=True)
    age = IntegerField()


if __name__ == "__main__":
    user = User(name="Juniven", age=30)
    print(user.to_dict())

    # test error
    user2 = User(age=12)
