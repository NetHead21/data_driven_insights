from models.model import Model
from fields.primarykey_field import PrimaryKeyField
from fields.string_field import StringField
from fields.integer_field import IntegerField


class User(Model):
    uid = PrimaryKeyField(auto=True)
    name = StringField(required=True)
    age = IntegerField()

    def clean(self) -> None:
        if self.age is not None and self.age < 18:
            raise ValueError("Age must be at least 18")

    def before_save(self) -> None:
        self.name = self.name.title()

    class Meta:
        table_name = "users_data.json"


if __name__ == "__main__":
    user1 = User(name="John Doe", age=30)
    user1.save()
    user2 = User(name="Jane Doe", age=25)
    user2.save()
    user3 = User(name="Juniven", age=30)
    user3.save()

    # user4 = User(name="Charlie", age=15)
    # user4.save()  # This will raise a ValueError

    users = User.all()
    for user in users:
        print(f"{user.name} is {user.age} years old")

    # test error
    # user2 = User(age=12)

    users = User.filter(name="John Doe")
    for user in users:
        print(f"Found user: {user.name} is {user.age} years old")

    # test error
    # user = User.get(name="Charlie")
