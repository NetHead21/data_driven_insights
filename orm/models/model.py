from typing import Any, Dict, List, Type
from fields.field import Field
import os
import json


class Model:
    """
    A base class for defining models with field validation and persistence.

    This class provides functionality for defining fields, validating data, and persisting
    model instances to a JSON file. It supports operations like saving, retrieving all records,
    filtering, and getting specific records.

    Example usage:
        >>> from fields.field import Field
        >>> class User(Model):
        ...     uid = Field(required=True)
        ...     name = Field(required=True)
        ...     age = Field(default=18)
        ...
        ...     class Meta:
        ...         table_name = "users.json"

        >>> # Create a new user
        >>> user = User(uid=1, name="Alice")
        >>> user.to_dict()
        {'uid': 1, 'name': 'Alice', 'age': 18}

        >>> # Save the user to the JSON file
        >>> user.save()

        >>> # Retrieve all users
        >>> users = User.all()
        >>> len(users) > 0
        True

        >>> # Filter users by name
        >>> filtered_users = User.filter(name="Alice")
        >>> len(filtered_users) == 1
        True

        >>> # Get a specific user
        >>> retrieved_user = User.get(uid=1)
        >>> retrieved_user.name
        'Alice'

        >>> # Attempt to get a non-existent user (raises ValueError)
        >>> User.get(uid=999)  # doctest: +IGNORE_EXCEPTION_DETAIL
        Traceback (most recent call last):
        ValueError: No User found with {'uid': 999}

        >>> # Attempt to create a user with missing required fields (raises ValueError)
        >>> User(name="Bob")  # doctest: +IGNORE_EXCEPTION_DETAIL
        Traceback (most recent call last):
        ValueError: Missing required fields ['uid'] in User

    Attributes:
        _fields_cache (Dict[Type["Model"], Dict[str, Field]]): A cache for storing field definitions
            for each model class.

    Methods:
        __init__(**kwargs):
            Initializes a new instance of the model, validates required fields, and sets default values.

        get_table_name() -> str:
            Returns the name of the JSON file associated with the model.

        _get_fields() -> Dict[str, Field]:
            Retrieves the field definitions for the model.

        to_dict() -> Dict[str, Any]:
            Converts the model instance to a dictionary.

        save():
            Saves the model instance to the JSON file.

        all() -> List["Model"]:
            Retrieves all records from the JSON file.

        _is_valid_entry(item: Dict[str, Any]) -> bool:
            Validates if a dictionary can be converted into a model instance.

        filter(**kwargs) -> List["Model"]:
            Filters records based on the provided keyword arguments.

        get(**kwargs) -> "Model":
            Retrieves a single record that matches the provided keyword arguments.
            Raises a ValueError if no record or multiple records are found.
    """

    _fields_cache: Dict[Type["Model"], Dict[str, Field]] = {}

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
    def get_table_name(cls) -> str:
        if hasattr(cls, "Meta") and hasattr(cls.Meta, "table_name"):
            return cls.Meta.table_name
        return f"{cls.__name__}.json"

    @classmethod
    def _get_fields(cls) -> Dict[str, Field]:
        if cls not in Model._fields_cache:
            Model._fields_cache[cls] = {
                key: field
                for key, field in cls.__dict__.items()
                if isinstance(field, Field)
            }
        return Model._fields_cache[cls]

    def to_dict(self) -> Dict[str, Any]:
        return {key: getattr(self, key) for key in self._get_fields()}

    def save(self):
        if hasattr(self, "before_save"):
            self.before_save()

        if hasattr(self, "clean"):
            self.clean()

        file_name = self.get_table_name()

        # Load existing data
        if os.path.exists(file_name):
            try:
                with open(file_name, "r") as file:
                    data = json.load(file)
            except json.JSONDecodeError:
                data = []
        else:
            data = []

        # Check for existing record and update
        record = self.to_dict()
        for i, item in enumerate(data):
            if item.get("uid") == record.get("uid"):
                data[i] = record
                break
        else:
            data.append(record)

        # Save updated data
        with open(file_name, "w") as file:
            json.dump(data, file, indent=2)

    @classmethod
    def all(cls) -> List["Model"]:
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
    def _is_valid_entry(cls, item: Dict[str, Any]) -> bool:
        try:
            cls(**item)
            return True
        except (TypeError, ValueError):
            return False

    @classmethod
    def filter(cls, **kwargs) -> List["Model"]:
        return [
            obj
            for obj in cls.all()
            if all(getattr(obj, key) == value for key, value in kwargs.items())
        ]

    @classmethod
    def get(cls, **kwargs) -> "Model":
        matches = cls.filter(**kwargs)
        if not matches:
            raise ValueError(f"No {cls.__name__} found with {kwargs}")

        if len(matches) > 1:
            raise ValueError(f"Multiple {cls.__name__} instances match {kwargs}")
        return matches[0]
