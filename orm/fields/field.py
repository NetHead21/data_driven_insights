from typing import Any, Optional, List, Callable


class ValidationError(Exception):
    """Custom exception for validation errors."""

    pass


class Field:
    def __init__(
        self,
        required: bool = False,
        default: Optional[Any] = None,
        max_length: Optional[int] = None,
        choices: Optional[List[Any]] = None,
        validator: Optional[Callable[[Any], bool]] = None,
    ) -> None:
        self.required = required
        self.default = default
        self.max_length = max_length
        self.choices = choices
        self.validator = validator

    def __set_name__(self, owner, name):
        self.private_name = "_" + name
        self.public_name = name

    def __get__(self, instance, owner):
        return getattr(instance, self.private_name, None)

    def __set__(self, instance, value):
        self.validate(value)
        setattr(instance, self.private_name, value)

    def validate(self, value: Any) -> None:
        """Validate the value against all constraints."""
        self._validate_max_length(value)
        self._validate_choices(value)
        self._validate_custom(value)

    def _validate_max_length(self, value: Any) -> None:
        if (
            self.max_length is not None
            and isinstance(value, str)
            and len(value) > self.max_length
        ):
            raise ValidationError(
                f"'{self.public_name}' exceeds maximum length of {self.max_length}. "
                f"Provided value: '{value}'"
            )

    def _validate_choices(self, value: Any) -> None:
        if self.choices is not None and value not in self.choices:
            raise ValidationError(
                f"'{self.public_name}' must be one of {self.choices}. "
                f"Provided value: '{value}'"
            )

    def _validate_custom(self, value: Any) -> None:
        if self.validator is not None and not self.validator(value):
            raise ValidationError(
                f"'{self.public_name}' failed custom validation. "
                f"Provided value: '{value}'"
            )
