# coding=utf-8
"""
InaSAFE Disaster risk assessment tool by AusAid -**ImpactCalculator.**

The module provides a high level interface for running SAFE scenarios.

Contact : ole.moller.nielsen@gmail.com

.. note:: This program is free software; you can redistribute it and/or modify
     it under the terms of the GNU General Public License as published by
     the Free Software Foundation; either version 2 of the License, or
     (at your option) any later version.

"""

__author__ = 'tim@kartoza.com, ole.moller.nielsen@gmail.com'
__revision__ = '$Format:%H$'
__date__ = '11/01/2011'
__copyright__ = ('Copyright 2012, Australia Indonesia Facility for '
                 'Disaster Reduction')

# This import is to enable SIP API V2
# noinspection PyUnresolvedReferences
import qgis  # pylint: disable=unused-import
# noinspection PyPackageRequirements
from PyQt4.QtCore import QObject

# Do not import any QGIS or SAFE modules in this module!
from safe.utilities.impact_calculator_thread import ImpactCalculatorThread
from safe.common.exceptions import (
    InsufficientParametersError,
    InvalidParameterError)
from safe.impact_functions.impact_function_manager import ImpactFunctionManager
from safe.impact_functions.base import ImpactFunction


class ImpactCalculator(QObject):
    """A class to compute an impact scenario."""

    # DK: I think it should be only one module that uses information about
    # function style:
    #  ImpactCalculator
    #     gets layers
    #     checks style of the impact function
    #     informs about layer clipping (is the clipping requires?)

    def __init__(self):
        """Constructor for the impact calculator."""
        QObject.__init__(self)
        self.impact_function_manager = ImpactFunctionManager()
        self._impact_function = None
        self._extent = None

    @property
    def impact_function(self):
        """Property for the impact_function instance.

        :returns: An impact function instance.
        :rtype: ImpactFunction
        """
        return self._impact_function

    @impact_function.setter
    def impact_function(self, function):
        """Setter for impact function property.

        :param function: A valid impact function.
        :type function: basestring, ImpactFunction
        """
        if isinstance(function, basestring):
            self._impact_function = self.impact_function_manager \
                .get(function)
        elif isinstance(function, ImpactFunction):
            self._impact_function = function
        else:
            message = self.tr('Error: Invalid Impact Function.')
            raise InvalidParameterError(message)

    def get_runner(self):
        """ Factory to create a new runner thread.

        Requires three parameters to be set before execution can take place:

        * Hazard layer - a path to a raster (string)
        * Exposure layer - a path to a vector hazard layer (string).
        * Function - a function name that defines how the Hazard assessment
          will be computed (string).

        :returns: An impact calculator thread instance.
        :rtype: ImpactCalculatorThread

        :raises: InsufficientParametersError if not all parameters are set.
        """
        if self.impact_function is None:
            message = self.tr('Error: Function not set.')
            raise InsufficientParametersError(message)

        if self.impact_function.hazard is None:
            message = self.tr('Error: Hazard layer not set.')
            raise InsufficientParametersError(message)

        if self.impact_function.exposure is None:
            message = self.tr('Error: Exposure layer not set.')
            raise InsufficientParametersError(message)

        return ImpactCalculatorThread(
            self._impact_function,
            extent=self.extent(),
            check_integrity=self.requires_clipping())

    def function(self):
        """Accessor for the impact function.

        :returns: An InaSAFE impact function or None depending on if it is set.
        :rtype: safe.impact_functions.base.ImpactFunction, None
        """
        return self._impact_function

    def requires_clipping(self):
        """Check to clip or not to clip layers.

        If self._function is a 'new-style' impact function, then
        return False -- clipping is unnecessary, else return True

        :returns:   To clip or not to clip.
        :rtype:     bool

        :raises: InsufficientParametersError if function parameter is not set.
                 InvalidParameterError if the function has unknown style.
        """
        if self._impact_function is None:
            message = self.tr('Error: Impact Function is not provided.')
            raise InsufficientParametersError(message)

        impact_function_type = \
            self.impact_function_manager.get_function_type(
                self._impact_function)
        if impact_function_type == 'old-style':
            return True
        elif impact_function_type == 'qgis2.0':
            return False
        else:
            message = self.tr('Error: Impact Function has unknown style.')
            raise InvalidParameterError(message)

    def set_extent(self, extent):
        """Mutator for the extent property.

        Set extent that can be used as bounding box of the
            calculator's working region.

        :param extent:  Bounding box [xmin, ymin, xmax, ymax]
            of the working region.
        :type extent: list, None

        """
        self._extent = extent

    def extent(self):
        """Accessor for the extent property.

        :returns: Bounding box [xmin, ymin, xmax, ymax] of the working region.
        :rtype: list, None
        """
        return self._extent
