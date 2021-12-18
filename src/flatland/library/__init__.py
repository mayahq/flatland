import os

__INTERNAL_DIR__ = os.path.dirname(os.path.abspath(__file__))


def internal_include(filename: str):
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
