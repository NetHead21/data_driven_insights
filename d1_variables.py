# Variable declaration
name = "Alice"
age = 30
height = 5.6
is_developer = True

# Display the values using print()
print(f"Name: {name}")
print(f"Age: {age}")
print(f"Height: {height}")
print(f"Is a Developer?: {is_developer}")

# Type checking
print(f"Type of name: {type(name)}")
print(f"Type of age: {type(age)}")
print(f"Type of height: {type(height)}")
print(f"Type of is_developer: {type(is_developer)}")

# Using formatted strings (f-strings)
print("My name is %s and I am %d years old." % (name, age))
print("My name is {} and I am {} years old.".format(name, age))
print(f"My name is {name} and I am {age} years old.")
