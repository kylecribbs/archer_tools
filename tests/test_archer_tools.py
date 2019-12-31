#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Tests for `archer_tools` package."""
import os

import pytest
from click.testing import CliRunner

import marshmallow
from archer_tools import ArcherTools, cli


@pytest.fixture
def client():
    """Pytest fixture for archer_tools."""
    client = ArcherTools()
    yield client


def test_good_config():
    """Test Good Config."""
    runner = CliRunner()
    filename = f"{os.getcwd()}/tests/config.yaml"
    print(filename)
    with runner.isolated_filesystem():
        run = runner.invoke(cli.cli, ["run", "-y", filename])
        assert run.exit_code == 0
        assert "Successfully" in run.output


def test_bad_config(client):
    """Sample pytest test function with the pytest fixture as an argument."""
    filename = f"{os.getcwd()}/tests/bad-config.yaml"
    with pytest.raises(marshmallow.exceptions.ValidationError):
        client.read_config(filename)


def test_command_line_interface():
    """Test the CLI."""
    runner = CliRunner()
    result = runner.invoke(cli.cli)
    assert result.exit_code == 0
    assert "Console script for archer_tools" in result.output
    help_result = runner.invoke(cli.cli, ["--help"])
    assert help_result.exit_code == 0
    assert "--help  Show this message and exit." in help_result.output
    schema_result = runner.invoke(cli.cli, ["schema", "--metadata"])
    assert schema_result.exit_code == 0
    assert "configuration:" in schema_result.output
    version_result = runner.invoke(cli.cli, ["version"])
    assert version_result.exit_code == 0
    assert "archer_tools version" in version_result.output
