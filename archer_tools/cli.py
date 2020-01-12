# -*- coding: utf-8 -*-

"""Console script for archer_tools."""
import logging

import click
import yaml
from marshmallow import fields

from archer_tools import ArcherTools, __version__
from archer_tools.config_schema import ConfigSchema


@click.group()
def cli():
    """Collect cli tools."""


@cli.command()
def version():
    """Print version."""
    click.echo(f"{__package__} version {__version__}")


@cli.command()
@click.option(
    "--metadata",
    is_flag=True,
    help="Show metadata about fields",
)
def schema(**kwargs):
    """Print Default Yaml Schema."""
    config_schema = ConfigSchema()
    config_fields = config_schema.__dict__['declared_fields']
    data = recurse_fields(config_fields, metadata=kwargs['metadata'])
    data = yaml.dump(data)
    click.echo(data)


def recurse_fields(data, metadata=False):
    """Recurse Schema Fields."""
    temp = {}
    for field in data:
        new_fields = data[field].__dict__
        if isinstance(data[field], fields.Nested):
            nested = new_fields['nested']()
            hold = recurse_fields(
                nested.__dict__['declared_fields'],
                metadata=metadata
            )
            if new_fields['many']:
                new_hold = []
                new_hold.append(hold)
                hold = new_hold
            temp.update({
                field: hold
            })
        else:
            new_data = "Value"
            if metadata:
                keep = ['required', 'allow_none', 'default']
                hold = {k: new_fields.pop(k) for k in keep}
                new_data = {'metadata': hold}
            temp.update({
                field: new_data
            })
    return temp


@cli.command()
@click.option(
    "--yaml",
    "-y",
    default="config.yaml",
    type=click.File(),
    help="Specify full path and name of the yaml config file.",
)
@click.option(
    "--dry-run",
    is_flag=True,
    help="This will only run the sources and not the destinations."
)
@click.option(
    "--ignore-source-failure",
    is_flag=True,
    help="If a source fails it will continue with the rest of them."
)
def run(**kwargs):
    """Console script for archer_tools.

    Args:
        yaml (click.File): Yaml file object

    Raises:
        click.ClickException: when some unknown error occurs

    """
    logger = logging.getLogger(__name__)
    try:
        archer_tools = ArcherTools()
        archer_tools.run(
            kwargs['yaml'],
            dry_run=kwargs['dry_run'],
            ignore_source_failure=kwargs['ignore_source_failure']
        )
    except Exception as exc:
        logger.exception(exc)
        raise click.ClickException("An error occured: %s" % exc)
