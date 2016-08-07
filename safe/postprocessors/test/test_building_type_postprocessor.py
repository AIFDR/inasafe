# -*- coding: utf-8 -*-
"""**Postprocessors package.**

Test building type postprocessor
"""

__author__ = 'Christian Christelis <christian@kartoza.com>'
__revision__ = '$Format:%H$'
__date__ = '21/07/2015'
__license__ = "GPL"
__copyright__ = 'Copyright 2012, Australia Indonesia Facility for '
__copyright__ += 'Disaster Reduction'


import unittest

from safe.postprocessors.building_type_postprocessor import (
    BuildingTypePostprocessor)

POSTPROCESSOR = BuildingTypePostprocessor()


class TestBuildingTypePostprocessor(unittest.TestCase):

    def tearDown(self):
        """Run after each test."""
        POSTPROCESSOR.clear()

    def test_process_integer_values(self):
        """Test for checking if the ratio is wrong (total is more than one)."""
        # ratios_total < 1 should pass
        params = {
            'impact_total': 0,
            'key_attribute': 'type',
            u'Building type': True,
            'target_field': 'safe_ag__4',
            'value_mapping': {u'government': [u'Government']},
            'impact_attrs': [
                {'type': 'Government', 'safe_ag__4': 1},
                {'type': 'Government', 'safe_ag__4': 0},
                {'type': 'Government', 'safe_ag__4': 1},
                {'type': 'Government', 'safe_ag__4': 0},
            ]}
        POSTPROCESSOR.setup(params)
        POSTPROCESSOR.process()
        results = POSTPROCESSOR.results()
        message = (
            'Expecting exactly 2 Government buildings to be affected. ',
            'Using integer values in affected fields.')
        self.assertEqual(
            results[u'Government']['value'],
            '2',
            message)

    def test_process_string_values(self):
        """Test for checking if the ratio is wrong (total is more than one)."""
        # ratios_total < 1 should pass
        params = {
            'impact_total': 0,
            'key_attribute': 'type',
            u'Building type': True,
            'target_field': 'safe_ag__4',
            'value_mapping': {u'government': [u'Government']},
            'impact_attrs': [
                {'type': 'Government', 'safe_ag__4': 'Zone 1'},
                {'type': 'Government', 'safe_ag__4': 'Not Affected'},
                {'type': 'Government', 'safe_ag__4': 'Zone 1'},
                {'type': 'Government', 'safe_ag__4': 'Not Affected'},
            ]}
        POSTPROCESSOR.setup(params)
        POSTPROCESSOR.process()
        results = POSTPROCESSOR.results()
        self.assertEqual(results[u'Government']['value'], '2')

    def test_total_affected_calculated_correctly(self):
        """Test to see that the totalling of buildings is done correctly."""
        # ratios_total < 1 should pass
        params = {
            'impact_total': 0,
            'key_attribute': 'type',
            u'Building type': True,
            'target_field': 'safe_ag__4',
            'value_mapping': {
                u'government': [u'Government'],
                u'economy': [u'Economy'],
            },
            'impact_attrs': [
                {'type': 'Government', 'safe_ag__4': 'Zone 1'},
                {'type': 'Museum', 'safe_ag__4': 'Zone 2'},
                {'type': 'Government', 'safe_ag__4': 'Zone 1'},
                {'type': 'Government', 'safe_ag__4': 'Not Affected'},
                {'type': 'School', 'safe_ag__4': 'Zone 3'},
            ]}
        POSTPROCESSOR.setup(params)
        POSTPROCESSOR.process()
        results = POSTPROCESSOR.results()
        self.assertEqual(results[u'Government']['value'], '2')
        self.assertEqual(results[u'Other']['value'], '2')

        POSTPROCESSOR.clear()
        # Same as above, but we add the school in the value mapping.
        params = {
            'impact_total': 0,
            'key_attribute': 'type',
            u'Building type': True,
            'target_field': 'safe_ag__4',
            'value_mapping': {
                u'government': [u'Government', u'School'],
                u'economy': [u'Economy'],
            },
            'impact_attrs': [
                {'type': 'Government', 'safe_ag__4': 'Zone 1'},
                {'type': 'Museum', 'safe_ag__4': 'Zone 2'},
                {'type': 'Government', 'safe_ag__4': 'Zone 1'},
                {'type': 'Government', 'safe_ag__4': 'Not Affected'},
                {'type': 'School', 'safe_ag__4': 'Zone 3'},
            ]}
        POSTPROCESSOR.setup(params)
        POSTPROCESSOR.process()
        results = POSTPROCESSOR.results()
        self.assertEqual(results[u'Government']['value'], '3')
        self.assertEqual(results[u'Other']['value'], '1')


if __name__ == '__main__':
    suite = unittest.makeSuite(TestBuildingTypePostprocessor, 'test')
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite)
