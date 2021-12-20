import os


def check_file(file):
    if os.path.exists(file) and os.path.isfile(file):
        return file
    raise ValueError(f"{file} is invalid")


def check_dir(s):
    if os.path.exists(s) and os.path.isdir(s):
        return os.path.abspath(s)
    raise NotADirectoryError(f"{s} is not a valid directory")
