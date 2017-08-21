# -*- coding: utf-8 -*-
from __future__ import division
from __future__ import print_function
from __future__ import absolute_import
# from __future__ import unicode_literals

from click.testing import CliRunner
from datapackage.cli import cli


# Tests

def test_cli_validate_valid():
    runner = CliRunner()
    result = runner.invoke(cli, ['validate', 'data/datapackage/datapackage.json'])
    assert result.exit_code == 0
    assert 'Data package descriptor is valid' in result.output


def test_cli_validate_invalid():
    runner = CliRunner()
    result = runner.invoke(cli, ['validate', 'data/data-package.json'])
    assert result.exit_code == 1
    assert 'Validation errors' in result.output


def test_cli_infer():
    runner = CliRunner()
    result = runner.invoke(cli, ['infer', 'data/datapackage/*.csv'])
    assert result.exit_code == 0
    assert 'tabular-data-package' in result.output


def test_cli_version():
    runner = CliRunner()
    result = runner.invoke(cli, ['--version'])
    assert result.exit_code == 0
    assert len(result.output.split('.')) == 3
