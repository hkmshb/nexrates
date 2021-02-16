from nexrates import get_version


def test_version():
    version = get_version()
    assert version is not None
    assert len(version.split('.')) in (3, 4)
