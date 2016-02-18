from __future__ import print_function

import click
import os
import sys
import codecs
import datapackage_validate


@click.command()
@click.argument('action')
@click.argument('datapackage')
def main(action, datapackage):
    if action=='validate':
        # is it a dir or the json file?
        if os.path.isdir(datapackage):
            json_path = os.path.join(datapackage, "datapackage.json")
        elif os.path.exists(datapackage):
            json_path = datapackage
        else:
            msg = "'%s' is neither an existing directory \
neither an existing file" % datapackage
            raise NotImplementedError(msg)
        json_contents = codecs.open(json_path, 'r', 'utf-8').read()

        try:
            datapackage_validate.validate(json_contents)
            # datapackage_validate.validate(json_contents, schema)
        except datapackage_validate.exceptions.DataPackageValidateException as e:
            n_errors = len(e.errors)
            if n_errors == 1:
                s = "%d error" % n_errors
            else:
                s = "%d error" % n_errors
            s += " found in datapackage.json:"
            for err in e.errors:
                s += " \n **ERROR** %s" % err
            print(s, file=sys.stderr)
    else:
        lst_actions_allowed = ['validate']
        msg = "action '%s' not in %s" % (action, lst_actions_allowed)
        raise NotImplementedError(msg)

if __name__ == '__main__':
    main()
