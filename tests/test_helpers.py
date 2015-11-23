import os


__FIXTURES_PATH = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    'fixtures'
)


def fixture_path(fixture):
    return os.path.join(__FIXTURES_PATH, fixture)
