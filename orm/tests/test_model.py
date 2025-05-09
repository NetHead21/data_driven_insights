import os
import pytest
import json
from orm.models.model import Model
from orm.fields.field import Field


class TestUser(Model):
    uid = Field(required=True)
    name = Field(required=True)
    age = Field(default=18)

    class Meta:
        table_name = "test_users.json"


@pytest.fixture(autouse=True)
def cleanup_test_file():
    """Cleanup the test JSON file after each test."""
    yield
    if os.path.exists(TestUser.get_table_name()):
        os.remove(TestUser.get_table_name())


def test_create_and_save_user():
    user = TestUser(uid=1, name="Alice")
    user.save()

    # Verify the user is saved in the JSON file
    with open(TestUser.get_table_name(), "r") as file:
        data = json.load(file)
    assert len(data) == 1
    assert data[0] == {"uid": 1, "name": "Alice", "age": 18}


def test_retrieve_all_users():
    user1 = TestUser(uid=1, name="Alice")
    user2 = TestUser(uid=2, name="Bob")
    user1.save()
    user2.save()

    users = TestUser.all()
    assert len(users) == 2
    assert users[0].name == "Alice"
    assert users[1].name == "Bob"


def test_filter_users():
    user1 = TestUser(uid=1, name="Alice")
    user2 = TestUser(uid=2, name="Bob")
    user1.save()
    user2.save()

    filtered_users = TestUser.filter(name="Alice")
    assert len(filtered_users) == 1
    assert filtered_users[0].uid == 1


def test_get_user():
    user = TestUser(uid=1, name="Alice")
    user.save()

    retrieved_user = TestUser.get(uid=1)
    assert retrieved_user.name == "Alice"


def test_get_user_not_found():
    with pytest.raises(ValueError, match="No TestUser found with {'uid': 999}"):
        TestUser.get(uid=999)


def test_get_multiple_users_error():
    user1 = TestUser(uid=1, name="Alice")
    user2 = TestUser(uid=2, name="Alice")
    user1.save()
    user2.save()

    with pytest.raises(
        ValueError, match="Multiple TestUser instances match {'name': 'Alice'}"
    ):
        TestUser.get(name="Alice")


def test_missing_required_field():
    with pytest.raises(
        ValueError, match="Missing required fields \\['uid'\\] in TestUser"
    ):
        TestUser(name="Alice")


def test_invalid_field():
    with pytest.raises(
        AttributeError,
        match="Invalid fields \\['invalid_field'\\] for class 'TestUser'",
    ):
        TestUser(uid=1, name="Alice", invalid_field="value")


def test_update_existing_user():
    user = TestUser(uid=1, name="Alice")
    user.save()

    # Update the user's name
    user.name = "Alice Updated"
    user.save()

    users = TestUser.all()
    assert len(users) == 1
    assert users[0].name == "Alice Updated"
