from typing import Any, Optional


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
