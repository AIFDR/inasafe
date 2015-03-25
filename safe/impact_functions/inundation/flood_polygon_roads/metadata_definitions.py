# coding=utf-8
from safe.common.utilities import OrderedDict
from safe.definitions import (
    hazard_definition,
    hazard_flood,
    unit_wetdry,
    layer_vector_polygon,
    exposure_definition,
    exposure_road,
    unit_road_type_type,
    layer_vector_line)
from safe.impact_functions.impact_function_metadata import \
    ImpactFunctionMetadata
from safe.utilities.i18n import tr


class FloodPolygonRoadsMetadata(ImpactFunctionMetadata):
    """Metadata for FloodVectorRoadsExperimentalFunction.

    .. versionadded:: 2.1

    We only need to re-implement get_metadata(), all other behaviours
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
            'id': 'FloodVectorRoadsExperimentalFunction',
            'name': tr('Flood Vector Roads Experimental Function'),
            'impact': tr('Be flooded'),
            'title': tr('Be flooded'),
            'function_type': 'qgis2.0',
            'author': 'Dmitry Kolesov',
            'date_implemented': 'N/A',
            'overview': tr('N/A'),
            'detailed_description': tr('N/A'),
            'hazard_input': '',
            'exposure_input': '',
            'output': '',
            'actions': '',
            'limitations': [],
            'citations': [],
            'categories': {
                'hazard': {
                    'definition': hazard_definition,
                    'subcategories': [hazard_flood],
                    'units': [unit_wetdry],
                    'layer_constraints': [layer_vector_polygon]
                },
                'exposure': {
                    'definition': exposure_definition,
                    'subcategories': [exposure_road],
                    'units': [unit_road_type_type],
                    'layer_constraints': [layer_vector_line]
                }
            },
            'parameters': OrderedDict([
                # This field of the exposure layer contains
                # information about road types
                ('road_type_field', 'TYPE'),
                # This field of the  hazard layer contains information
                # about inundated areas
                ('affected_field', 'affected'),
                # This value in 'affected_field' of the hazard layer
                # marks the areas as inundated
                ('affected_value', '1'),
                ('postprocessors', OrderedDict([('RoadType', {'on': True})]))
            ])
        }
        return dict_meta
