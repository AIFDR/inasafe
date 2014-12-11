# coding=utf-8
"""InaSAFE Disaster risk assessment tool developed by AusAid -
**IS Safe Interface.**

The purpose of the module is to centralise interactions between the gui
package and the underlying InaSAFE packages. This should be the only place
where SAFE modules are imported directly.

Contact : ole.moller.nielsen@gmail.com

.. note:: This program is free software; you can redistribute it and/or modify
     it under the terms of the GNU General Public License as published by
     the Free Software Foundation; either version 2 of the License, or
     (at your option) any later version.

"""

__author__ = 'tim@linfiniti.com, ole.moller.nielsen@gmail.com'
__revision__ = '$Format:%H$'
__date__ = '04/04/2012'
__copyright__ = ('Copyright 2012, Australia Indonesia Facility for '
                 'Disaster Reduction')


# Standard modules
import os
import unicodedata
import logging

# SAFE functionality - passed on to QGIS modules
# pylint: disable=W0611

# We want all these imports as they for part of the API wrapper used by other
# modules in safe_qgis
# noinspection PyUnresolvedReferences

from safe.api import (
    load_plugins,
    get_admissible_plugins,
    get_function_title,
    get_plugins as safe_get_plugins,
    read_keywords, bbox_intersection,
    write_keywords as safe_write_keywords,
    read_layer as safe_read_layer,
    buffered_bounding_box,
    verify as verify_util,
    VerificationError,
    InaSAFEError,
    temp_dir,
    unique_filename,
    safe_tr as safeTr,
    get_free_memory,
    calculate_impact as safe_calculate_impact,
    BoundingBoxError,
    GetDataError,
    ReadLayerError,
    PostProcessorError,
    get_plugins, get_version,
    in_and_outside_polygon as points_in_and_outside_polygon,
    calculate_polygon_centroid,
    get_postprocessors,
    get_postprocessor_human_name,
    format_int,
    get_unique_values,
    get_plugins_as_table,
    evacuated_population_weekly_needs,
    evacuated_population_needs,
    Layer,
    Vector,
    Raster,
    nan_allclose,
    DEFAULTS,
    messaging,
    DYNAMIC_MESSAGE_SIGNAL,
    STATIC_MESSAGE_SIGNAL,
    ERROR_MESSAGE_SIGNAL,
    BUSY_SIGNAL,
    NOT_BUSY_SIGNAL,
    ANALYSIS_DONE_SIGNAL,
    ErrorMessage,
    ZeroImpactException,
    PointsInputError,
    get_decimal_separator,
    get_thousand_separator,
    styles,
    feature_attributes_as_dict,
    get_utm_epsg,
    which,
    safe_to_qgis_layer,
    generate_iso_metadata,
    ISO_METADATA_KEYWORD_TAG)
# noinspection PyUnresolvedReferences
# hack for excluding test-related import in builded package

try:
    from safe.api import (
        HAZDATA, EXPDATA, TESTDATA, UNITDATA, BOUNDDATA)
except ImportError:
    pass
# pylint: enable=W0611

# InaSAFE GUI specific functionality
from PyQt4.QtCore import QCoreApplication

LOGGER = logging.getLogger('InaSAFE')


def tr(text):
    """We define a tr() alias here since the is_safe_interface implementation
    below is not a class and does not inherit from QObject.

    .. note:: see http://tinyurl.com/pyqt-differences

    Args:
       theText - string to be translated
    Returns:
       Translated version of the given string if available, otherwise
       the original string.
    """
    context = "@default"
    return QCoreApplication.translate(context, text)





def write_keywords_to_file(filename, keywords):
    """Thin wrapper around the safe write_keywords function.

    Args:
        * filename - str representing path to layer that must be written.
          If the file does not end in .keywords, its extension will be
          stripped off and the basename + .keywords will be used as the file.
        * keywords - a dictionary of keywords to be written
    Returns:
        None
    Raises:
        Any exceptions are propogated
    """
    basename, extension = os.path.splitext(filename)
    if 'keywords' not in extension:
        filename = basename + '.keywords'
    try:
        safe_write_keywords(keywords, filename)
    except:
        raise


def make_ascii(x):
    """Convert QgsString to ASCII"""
    x = unicode(x)
    x = unicodedata.normalize('NFKD', x).encode('ascii', 'ignore')
    return x


def get_safe_impact_function(function=None):
    """Thin wrapper around the safe impact_functions function.

    Args:
        function - optional str giving a specific plugins name that should
        be fetched.
    Returns:
        A safe impact function is returned
    Raises:
        Any exceptions are propagated
    """
    try:
        return safe_get_plugins(make_ascii(function))
    except:
        raise


def get_safe_impact_function_type(function_id):
    """
    Args:
        function_id - str giving a specific plugins name that should be
        fetched.
    Returns:
        A str type of safe impact function is returned:
            'old-style' is "classic" safe impact function
            'qgis2.0'   is impact function with native qgis layers support
    Raises:
        Any exceptions are propagated
    """
    try:
        # Get an instance of the impact function and get the type
        function = get_safe_impact_function(function_id)[0][function_id]
        function = function()

        try:
            fun_type = function.get_function_type()
        except AttributeError:
            fun_type = 'old-style'
    except:
        raise

    return fun_type
