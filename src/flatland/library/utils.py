import os

__INTERNAL_DIR__ = os.path.dirname(os.path.abspath(__file__))


def get_internal_dir():
    global __INTERNAL_DIR__
    return __INTERNAL_DIR__


def set_internal_dir(directory):
    global __INTERNAL_DIR__
    directory = os.path.abspath(directory)
    if os.path.exists(directory) and os.path.isdir(directory):
        __INTERNAL_DIR__ = directory
    else:
        raise NotADirectoryError(f"could not set directory as {directory}")


def check_internal_dir(filename: str):
    basename = os.path.basename(filename)
    if basename != filename:
        # this is a relative include, for user files
        return False, os.path.abspath(filename)

    localname = os.path.join(__INTERNAL_DIR__, filename)
    if os.path.exists(localname) and os.path.isfile(localname):
        # the user expects a file from the internal library
        return True, localname

    # don't know what to do
    return False, os.path.abspath(filename)
