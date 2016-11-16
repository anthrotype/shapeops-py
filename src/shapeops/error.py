from __future__ import print_function, division, absolute_import
from __future__ import unicode_literals


class ShapeOpsError(Exception):
    """Base ShapeOps exception"""


class InvalidContourError(ShapeOpsError):
    """Rased when an input contour is invalid"""


class InvalidSubjectContourError(InvalidContourError):
    """Rased when a 'subject' contour is not valid"""


class InvalidClippingContourError(InvalidContourError):
    """Rased when a 'clipping' contour is not valid"""


class ExecutionError(ShapeOpsError):
    """Raised when clipping execution fails"""
