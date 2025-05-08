from fields.field import Field


class StringField(Field):
    def __set__(self, instance, value):
        if not isinstance(value, str):
            raise TypeError("Expected a string")
        super().__set__(instance, value)
