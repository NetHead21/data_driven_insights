import pytest
from orm.fields.field import Field, ValidationError


def test_field_default_value():
    field = Field(default="default_value")

    class TestModel:
        test_field = field

    instance = TestModel()
    assert instance.test_field is None  # Default is not set automatically


def test_field_required_validation():
    field = Field(required=True)

    class TestModel:
        test_field = field

    instance = TestModel()
    with pytest.raises(ValidationError):
        instance.test_field = None  # Required field cannot be None


def test_field_max_length_validation():
    field = Field(max_length=5)

    class TestModel:
        test_field = field

    instance = TestModel()
    instance.test_field = "short"  # Valid
    with pytest.raises(ValidationError):
        instance.test_field = "too_long"  # Exceeds max_length


def test_field_choices_validation():
    field = Field(choices=["choice1", "choice2"])

    class TestModel:
        test_field = field

    instance = TestModel()
    instance.test_field = "choice1"  # Valid
    with pytest.raises(ValidationError):
        instance.test_field = "invalid_choice"  # Not in choices


def test_field_custom_validator():
    field = Field(validator=lambda x: x > 0)

    class TestModel:
        test_field = field

    instance = TestModel()
    instance.test_field = 10  # Valid
    with pytest.raises(ValidationError):
        instance.test_field = -1  # Fails custom validation


def test_field_combined_validations():
    field = Field(
        required=True, max_length=5, choices=["valid"], validator=lambda x: x.islower()
    )

    class TestModel:
        test_field = field

    instance = TestModel()
    instance.test_field = "valid"  # Valid
    with pytest.raises(ValidationError):
        instance.test_field = "INVALID"  # Fails custom validator
    with pytest.raises(ValidationError):
        instance.test_field = "toolong"  # Exceeds max_length
    with pytest.raises(ValidationError):
        instance.test_field = "other"  # Not in choices
