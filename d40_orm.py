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
