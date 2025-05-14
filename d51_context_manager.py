with open("data.txt", "w") as f:
    f.write("Hello, world!")

# The file is automatically closed even if an error occurs

class FileLogger:
    def __init__(self, filename: str):
        self.filename = filename

    def __enter__(self):
        self.file = open(self.filename, "a")
        return self.file

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.file.write(">> Logging session ended.\n")
        self.file.close()


with FileLogger("log.txt") as log:
    log.write(">> Loging session started.\n")
