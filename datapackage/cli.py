# -*- coding: utf-8 -*-
from __future__ import division
from __future__ import print_function
from __future__ import absolute_import
# from __future__ import unicode_literals

import click
import json
import datapackage
click.disable_unicode_literals_warning = True


# Module API

@click.group()
@click.version_option(datapackage.__version__, message='%(version)s')
def cli():
    pass


@cli.command()
@click.argument('descriptor', type=click.STRING)
def validate(descriptor):
    try:
        datapackage.validate(descriptor)
        click.echo('Data package descriptor is valid')
    except datapackage.exceptions.ValidationError as exception:
        click.echo('Data package descriptor is invalid')
        for error in exception.errors:
            click.echo(error)
        exit(1)


@cli.command()
@click.argument('pattern', type=click.STRING)
def infer(pattern):
    descriptor = datapackage.infer(pattern, base_path='.')
    click.echo(json.dumps(descriptor, indent=2))


# Main program

if __name__ == '__main__':
    cli()
