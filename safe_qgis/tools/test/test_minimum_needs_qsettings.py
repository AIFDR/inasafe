# coding=utf-8
"""
Minimum Needs Tool Test Cases.

InaSAFE Disaster risk assessment tool developed by AusAid and World Bank

Contact : christian@kartoza.com

.. note:: This program is free software; you can redistribute it and/or modify
     it under the terms of the GNU General Public License as published by
     the Free Software Foundation; either version 2 of the License, or
     (at your option) any later version.

"""

__author__ = 'Christian Christelis <christian@kartoza.com>'
__date__ = '14/09/2012'
__copyright__ = ('Copyright 2012, Australia Indonesia Facility for '
                 'Disaster Reduction')

import unittest

from PyQt4.QtCore import QSettings

from safe_qgis.tools.minimum_needs import QMinimumNeeds
from safe.common.minimum_needs import MinimumNeeds


class TestQMinimumNeeds(QMinimumNeeds):
    # noinspection PyMissingConstructor
    def __init__(self, test_profile='Test Minimum Needs Settings'):
        self.settings = QSettings(test_profile)
        self.settings.clear()
        self.settings = QSettings(test_profile)
        minimum_needs = self._defaults()
        minimum_needs['provenance'] = 'Test'
        minimum_needs['profile'] = 'Test'
        self.minimum_needs = minimum_needs


class MinimumNeedsTest(unittest.TestCase):
    """Test class to test QMinimum needs."""

    def setUp(self):
        """Test initialisation run before each test."""
        self.minimum_needs = TestQMinimumNeeds()

    def tearDown(self):
        """Run after each test."""
        self.minimum_needs.settings.clear()

    def test_01_loading_defaults(self):
        """Test loading the defaults on a blank settings."""
        full_minimum_needs = self.minimum_needs.get_full_needs()
        default_minimum_needs = MinimumNeeds._defaults()
        self.assertEqual(cmp(full_minimum_needs, default_minimum_needs), 0)

    def test_02_update_minimum_needs(self):
        """Change minimum needs and verify that the saved result are updated."""
        original_old = self.minimum_needs.get_full_needs()
        new_minimum_needs = {
            'resources': [{
                "Default": "5",
                "Minimum allowed": "1",
                "Maximum allowed": "10",
                "Frequency": "weekly",
                "Resource name": "Test resource",
                "Resource description": "Basic food",
                "Unit": "kilogram",
                "Units": "kilograms",
                "Unit abbreviation": "kg",
                "Readable sentence": "A displaced person should be provided with {{ Default }} {{ Unit }}/{{ Units }}/{{ Unit abbreviation }} of {{ Resource name }}. Though no less than {{ Minimum allowed }} and no more than {{ Maximum allowed }}. This should be provided {{ Frequency }}."
            }],
            'provenance': "Test",
            'profile': "Test"
        }
        self.minimum_needs.update_minimum_needs(new_minimum_needs)
        other_minimum_needs = TestQMinimumNeeds(test_profile='Other Test')
        other_old = other_minimum_needs.get_full_needs()

        self.minimum_needs.save()
        other_minimum_needs.load()
        other_new = other_minimum_needs.get_full_needs()
        original_new = self.minimum_needs.get_full_needs()

        # cmp compares dicts 0 == same, -1 == different
        self.assertEqual(cmp(original_old, other_old), 0)
        self.assertEqual(cmp(original_old, original_new), -1)
        self.assertEqual(cmp(other_old, other_new), -1)
        self.assertEqual(cmp(original_new, other_new), 0)






