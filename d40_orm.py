class Field:
    def __init__(self, required=False):
        self.required = required

    def __stet_name__(self, owner, name):
        self.private_name = "=" + name

    def __get__(self, instance, owner):
        return getattr(instance, self.private_name, None)

    def __set__(self, instance, value):
        setattr(instance, self.private_name, value)


class StringField(Field):
    def __set__(self, instance, value):
        if not instance(value, str):
            raise TypeError("Expected a string")
        super().__set__(instance, value)


class IntegerFrield(Field):
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
            for key in self.__class__.__dict__
            if isinstance(getattr(self.__class__, key), Field)
        }
