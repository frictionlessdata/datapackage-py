# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from .package import Package


# Module API


def validate(descriptor):
    '''Validate a data package descriptor.

    Args:
        descriptor (Union[str, dict]): Local or remote path to the descriptor,
            or the descriptor itself as a dict.

    Returns:
        bool: `True` if the descriptor is valid.

    Raises:
        `exceptions.ValidationError`: If the descriptor is invalid.
    '''
    Package(descriptor, strict=True)
    return True
