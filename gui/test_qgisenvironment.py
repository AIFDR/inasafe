"""
InaSafe Disaster risk assessment tool developed by AusAid - **RiabClipper test suite.**

Contact : ole.moller.nielsen@gmail.com

.. note:: This program is free software; you can redistribute it and/or modify
     it under the terms of the GNU General Public License as published by
     the Free Software Foundation; either version 2 of the License, or
     (at your option) any later version.

"""

__author__ = 'tim@linfiniti.com'
__version__ = '0.2.0'
__date__ = '20/01/2011'
__copyright__ = ('Copyright 2012, Australia Indonesia Facility for '
                 'Disaster Reduction')

import unittest
from qgis.core import QgsProviderRegistry
from utilities_test import getQgisTestApp

QGISAPP = getQgisTestApp()


class RiabTest(unittest.TestCase):
    """Test the QGIS Environment"""

    def test_QGISEnvironment(self):
        """QGIS environment has the expected providers"""

        r = QgsProviderRegistry.instance()
        #for item in r.providerList():
        #    print str(item)

        #print 'Provider count: %s' % len(r.providerList())
        assert 'gdal' in r.providerList()
        assert 'ogr' in r.providerList()

        # FIXME (Ole): When we start using PostGIS and WFS we
        #              can add more tests

if __name__ == '__main__':
    unittest.main()
