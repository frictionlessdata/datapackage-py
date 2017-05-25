# coding: utf-8
from __future__ import print_function
from __future__ import absolute_import
from __future__ import unicode_literals

import argparse
import os
import sys
import six

import datapackage
import datapackage.exceptions


class Command(object):

    def __init__(self, subparsers, command, stdout, stderr):
        self.stdout = stdout
        self.stderr = stderr
        parser = subparsers.add_parser(command)
        self.add_arguments(parser)
        parser.set_defaults(func=self.run)

    def add_arguments(self, parser):
        pass  # pragma: no cover

    def info(self, message):
        self.stdout.write(message.encode('utf-8') + b'\n')

    def error(self, message):
        self.stderr.write(message.encode('utf-8') + b'\n')

    def run(self):
        raise NotImplementedError


class Validate(Command):

    def add_arguments(self, parser):
        parser.add_argument('datapackage')

    def run(self, args):
        if os.path.isdir(args.datapackage):
            json_path = os.path.join(args.datapackage, "datapackage.json")
        elif os.path.exists(args.datapackage):
            json_path = args.datapackage
        else:
            self.error((
                "Error: '%s' is neither an existing directory neither an "
                "existing file."
            ) % args.datapackage)
            return 1

        try:
            datapackage.DataPackage(json_path).validate()
        except datapackage.exceptions.ValidationError as e:
            self.error('Error: %s' % e.message)
            return 1
        else:
            self.info('valid')


def main(argv=None, stdout=None, stderr=None):
    if six.PY3:
        stdout = stdout or sys.stdout.buffer
        stderr = stderr or sys.stderr.buffer
    else:  # pragma: no cover
        stdout = stdout or sys.stdout
        stderr = stderr or sys.stderr

    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers()

    Validate(subparsers, 'validate', stdout, stderr)

    args = parser.parse_args(argv)
    exit_code = args.func(args) or 0
    sys.exit(exit_code)


if __name__ == '__main__':
    main()
