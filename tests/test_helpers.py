import os
import shutil
import tempfile
from importlib import import_module
module = import_module('datapackage.helpers')


__FIXTURES_PATH = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    'fixtures'
)

def fixture_path(fixture, *paths):
    return os.path.join(__FIXTURES_PATH, fixture, *paths)


def test_ensure_dir():
    base_path = tempfile.mkdtemp()
    try:
        dir_path = os.path.join(base_path, 'dir')
        file_path = os.path.join(dir_path, 'file')
        assert not os.path.isdir(dir_path)
        module.ensure_dir(file_path)
        assert os.path.isdir(dir_path)
    finally:
        shutil.rmtree(base_path)
