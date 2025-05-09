from typing import Any, Optional, List, Callable


class ValidationError(Exception):
    """Custom exception for validation errors."""

    pass


class Field:
    """
    A descriptor class for defining and validating fields in a model.

    Attributes:
        required (bool): Indicates if the field is mandatory. Defaults to False.
        default (Optional[Any]): The default value for the field if not provided. Defaults to None.
        max_length (Optional[int]): The maximum length of the field's value (applicable to strings). Defaults to None.
        choices (Optional[List[Any]]): A list of valid values for the field. Defaults to None.
        validator (Optional[Callable[[Any], bool]]): A custom validation function that takes the field's value
            and returns True if valid, False otherwise. Defaults to None.

    Methods:
        __set_name__(owner, name):
            Sets the private and public names for the field when the class is created.

        __get__(instance, owner):
            Retrieves the value of the field from the instance.

        __set__(instance, value):
            Validates and sets the value of the field on the instance.

        validate(value: Any):
            Validates the value against all constraints (required, max_length, choices, custom validator).

        _validate_max_length(value: Any):
            Validates that the value does not exceed the maximum length (if applicable).

        _validate_choices(value: Any):
            Validates that the value is one of the allowed choices (if applicable).

        _validate_custom(value: Any):
            Validates the value using a custom validation function (if provided).
    """

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
        if self.required and value is None:
            raise ValidationError(
                f"'{self.public_name}' is required and cannot be None."
            )
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
