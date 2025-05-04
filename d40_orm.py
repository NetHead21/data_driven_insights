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
    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            if not hasattr(self.__class__, key):
                raise AttributeError(f"Unknown field: {key}")
            setattr(self, key, value)

    def to_dict(self):
        return {
            key: getattr(self, key)
            for key, field in self.__class__.__dict__.items()
            if isinstance(field, Field)
        }


class User(Model):
    name = StringField(required=True)
    age = IntegerField()


if __name__ == "__main__":
    user = User(name="Juniven", age=30)
    print(user.to_dict())
