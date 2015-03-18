# coding=utf-8
"""
InaSAFE Disaster risk assessment tool developed by AusAid and World Bank
- **Test for Flood Vector Building Impact Function.**

Contact : ole.moller.nielsen@gmail.com

.. note:: This program is free software; you can redistribute it and/or modify
     it under the terms of the GNU General Public License as published by
     the Free Software Foundation; either version 2 of the License, or
     (at your option) any later version.

"""
from safe.utilities.qgis_layer_wrapper import QgisWrapper

__author__ = 'lucernae'
__date__ = '11/12/2014'
__copyright__ = ('Copyright 2012, Australia Indonesia Facility for '
                 'Disaster Reduction')

import os
import unittest

from safe.impact_functions.registry import Registry
from safe.impact_functions.inundation.flood_building_impact_qgis\
    .impact_function import FloodNativePolygonExperimentalFunction
from safe.storage.core import read_layer
from safe.test.utilities import TESTDATA, get_qgis_app, clone_shp_layer
from safe.definitions import (
    unit_wetdry,
    layer_vector_polygon,
    exposure_structure,
    unit_building_type_type,
    hazard_flood)

QGIS_APP, CANVAS, IFACE, PARENT = get_qgis_app()


class TestFloodBuildingImpactQgisFunction(unittest.TestCase):
    """Test for Flood Vector Building Impact Function."""

    def setUp(self):
        self.registry = Registry()
        self.registry.register(FloodNativePolygonExperimentalFunction)

    def test_run(self):
        function = self.registry.get('FloodNativePolygonExperimentalFunction')

        building = 'test_flood_building_impact_exposure'
        flood_data = 'test_flood_building_impact_hazard'

        hazard_filename = os.path.join(TESTDATA, flood_data)
        exposure_filename = os.path.join(TESTDATA, building)
        hazard_layer = clone_shp_layer(
            name=hazard_filename,
            include_keywords=True,
            source_directory=TESTDATA)
        exposure_layer = clone_shp_layer(
            name=exposure_filename,
            include_keywords=True,
            source_directory=TESTDATA)

        function.hazard = QgisWrapper(hazard_layer)
        function.exposure = QgisWrapper(exposure_layer)
        function.extent = [106.8139860, -6.2043560,
                           106.8405950, -6.2263570]
        function.parameters['affected_field'] = 'FLOODPRONE'
        function.parameters['affected_value'] = 'YES'
        function.run()
        impact_layer = function.impact

        # Check the question
        expected_question = ('In the event of a flood in jakarta how many osm '
                             'building polygons might be flooded ('
                             'experimental)')
        message = 'The question should be %s, but it returns %s' % (
            expected_question, function.question())
        self.assertEqual(expected_question, function.question(), message)

        # Extract calculated result
        keywords = impact_layer.get_keywords()
        buildings_total = keywords['buildings_total']
        buildings_affected = keywords['buildings_affected']

        self.assertEqual(buildings_total, 67)
        self.assertEqual(buildings_affected, 41)

    def test_filter(self):
        hazard_keywords = {
            'subcategory': hazard_flood,
            'units': unit_wetdry,
            'layer_constraints': layer_vector_polygon
        }

        exposure_keywords = {
            'subcategory': exposure_structure,
            'units': unit_building_type_type,
            'layer_constraints': layer_vector_polygon
        }

        impact_functions = self.registry.filter(
            hazard_keywords, exposure_keywords)
        message = 'There should be 1 impact function, but there are: %s' % \
                  len(impact_functions)
        self.assertEqual(1, len(impact_functions), message)
