from importlib import metadata


def get_version():
    """Returns the package version details."""
    return metadata.version('nexrates')
