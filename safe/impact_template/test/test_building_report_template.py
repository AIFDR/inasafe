# coding=utf-8
"""
InaSAFE Disaster risk assessment tool developed by AusAid and World Bank
- **Building Report Template Test Cases.**

.. note:: This program is free software; you can redistribute it and/or modify
     it under the terms of the GNU General Public License as published by
     the Free Software Foundation; either version 2 of the License, or
     (at your option) any later version.

"""
__author__ = 'ismailsunni'
__project_name__ = 'inasafe-dev'
__filename__ = 'test_building_report_template'
__date__ = '4/15/16'
__copyright__ = 'imajimatika@gmail.com'

import unittest
import os
import json
from pprint import pprint

from safe.impact_template.building_report_template import (
    BuildingReportTemplate)

JSON_FILE = os.path.join('data', 'building_impact.json')


class TestBuildingReportTemplate(unittest.TestCase):
    def test_building_report_template(self):
        """Test Building Report Template
        """
        with open(JSON_FILE) as json_file:
            impact_data = json.load(json_file)

        building_report_template = BuildingReportTemplate(impact_data)
        html_report = building_report_template.generate_html_report()
        print html_report
        # self.assertEqual(True, False)


if __name__ == '__main__':
    unittest.main()
