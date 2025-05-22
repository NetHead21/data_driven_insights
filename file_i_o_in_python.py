# Caption: Read from and write to files effortlessly

# Why use File I/O?
# * Persist data to disk
# * Read configuration and logs
# * Exchange data between programs

import json
import csv
import pickle
from pathlib import Path


# Stub for line-by-line processing
def process(line: str) -> None:
    """Process a line of text."""
    pass


# Read entire file safely
try:
    with open("data.txt", "r", encoding="utf-8") as file:
        content = file.read()
except FileNotFoundError as e:
    print(f"Error: data.txt not found! {e}")


# Read line by line safely
try:
    with open("data.txt", "r", encoding="utf-8") as file:
        for line in file:
            process(line.rstrip("\n"))
except FileNotFoundError as e:
    print(f"Error: data.txt not found! {e}")


# Write text to a new file
with open("output.txt", "w", encoding="utf-8") as file:
    file.write("Hello, world!\n")


# Append text to an existing file
with open("output.txt", "a", encoding="utf-8") as file:
    file.write("Additional line\n")


# JSON serialization
with open("data.json", "w", encoding="utf-8") as file:
    json.dump("{"name": "Bob", "age": 30}, file)

