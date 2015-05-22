# coding=utf-8
"""InaSAFE Disaster risk tool by Australian Aid - Metadata for Flood Polygon
on Population Impact Function.

Contact : ole.moller.nielsen@gmail.com

.. note:: This program is free software; you can redistribute it and/or modify
     it under the terms of the GNU General Public License as published by
     the Free Software Foundation; either version 2 of the License, or
     (at your option) any later version.

"""

__author__ = 'Rizky Maulana Nugraha'

from safe.common.utilities import OrderedDict
from safe.defaults import (
    default_minimum_needs,
    default_provenance,
    default_gender_postprocessor,
    age_postprocessor,
    minimum_needs_selector)
from safe.impact_functions.impact_function_metadata import \
    ImpactFunctionMetadata
from safe.utilities.i18n import tr
from safe.new_definitions import (
    layer_mode_classified,
    layer_mode_continuous,
    layer_geometry_polygon,
    layer_geometry_raster,
    hazard_flood,
    hazard_category_single_hazard,
    flood_vector_hazard_classes,
    count_exposure_unit,
    exposure_population
)


class FloodEvacuationVectorHazardMetadata(ImpactFunctionMetadata):
    """Metadata for FloodEvacuationFunctionVectorHazard.

    .. versionadded:: 2.1

    We only need to re-implement as_dict(), all other behaviours
    are inherited from the abstract base class.
    """

    @staticmethod
    def as_dict():
        """Return metadata as a dictionary.

        This is a static method. You can use it to get the metadata in
        dictionary format for an impact function.

        :returns: A dictionary representing all the metadata for the
            concrete impact function.
        :rtype: dict
        """
        dict_meta = {
            'id': 'FloodEvacuationVectorHazardFunction',
            'name': tr('Flood Evacuation Vector Hazard Function'),
            'impact': tr('Need evacuation'),
            'title': tr('Need evacuation'),
            'function_type': 'old-style',
            'author': 'AIFDR',
            'date_implemented': 'N/A',
            'overview': tr(
                'To assess the impacts of flood inundation in vector '
                'format on population.'),
            'detailed_description': tr(
                'The population subject to inundation is determined '
                'whether in an area which affected or not. You can also '
                'set an evacuation percentage to calculate how many '
                'percent of the total population affected to be '
                'evacuated. This number will be used to estimate needs'
                ' based on BNPB Perka 7/2008 minimum bantuan.'),
            'hazard_input': tr(
                'A hazard vector layer which has attribute affected the '
                'value is either 1 or 0'),
            'exposure_input': tr(
                'An exposure raster layer where each cell represent '
                'population count.'),
            'output': tr(
                'Vector layer contains people affected and the minimum '
                'needs based on evacuation percentage.'),
            'actions': tr(
                'Provide details about how many people would likely need '
                'to be evacuated, where they are located and what '
                'resources would be required to support them.'),
            'limitations': [],
            'citations': [],
            'layer_requirements': {
                'hazard': {
                    'layer_mode': layer_mode_classified,
                    'layer_geometries': [layer_geometry_polygon],
                    'hazard_categories': [hazard_category_single_hazard],
                    'hazard_types': [hazard_flood],
                    'continuous_hazard_units': [],
                    'vector_hazard_classifications': [
                        flood_vector_hazard_classes],
                    'raster_hazard_classifications': []
                },
                'exposure': {
                    'layer_mode': layer_mode_continuous,
                    'layer_geometries': [layer_geometry_raster],
                    'exposure_types': [exposure_population],
                    'exposure_units': [count_exposure_unit]
                }
            },
            'parameters': OrderedDict([
                # Percent of affected needing evacuation
                ('evacuation_percentage', 1),
                ('postprocessors', OrderedDict([
                    ('Gender', default_gender_postprocessor()),
                    ('Age', age_postprocessor()),
                    ('MinimumNeeds', minimum_needs_selector()),
                ])),
                ('minimum needs', default_minimum_needs()),
                ('provenance', default_provenance())
            ])
        }
        return dict_meta
