'''
Disaster risk assessment tool developed by AusAid - **QGIS plugin test suite.**

Contact : ole.moller.nielsen@gmail.com

.. note:: This program is free software; you can redistribute it and/or modify
     it under the terms of the GNU General Public License as published by
     the Free Software Foundation; either version 2 of the License, or
     (at your option) any later version.

'''

__author__ = 'tim@linfiniti.com'
__version__ = '0.0.1'
__date__ = '10/01/2011'
__copyright__ = ('Copyright 2012, Australia Indonesia Facility for '
                 'Disaster Reduction')

import os
from riabexceptions import QgisPathException

# Check if a qgispath.txt file exists in the plugin folder (you
# need to rename it from qgispath.txt.templ in the standard plugin
# distribution) and if it does, read the qgis path

ROOT = os.path.dirname(__file__)
PATH = os.path.abspath(os.path.join(ROOT, 'qgispath.txt'))
QGIS_PATH = None #e.g. /usr/local if QGIS is installed under there
if os.path.isfile(PATH):
    try:
        QGIS_PATH = file(PATH, 'rt').readline().rstrip()
        sys.path.append(os.path.join(QGIS_PATH, 'share', 'qgis', 'python'))
        print sys.path
    except Exception, e:
        raise QgisPathException
    
from qgis.core import QgsApplication
from qgis.gui import QgsMapCanvas
from qgisinterface import QgisInterface
import unittest
from PyQt4.QtGui import QApplication, QWidget
from PyQt4.QtTest import QTest
from PyQt4.QtCore import Qt
from riab import Riab

class RiabTest(unittest.TestCase):
    """Test the risk in a box plugin stub"""

    def setUp(self):
        """Create an app that all tests can use"""
        myGuiFlag = True  # We need to enable qgis app in gui mode
        self.app = QgsApplication(sys.argv, True)
        #todo - softcode these paths
        self.app.setPrefixPath('/usr/local')
        self.app.setPluginPath('/usr/local/lib/qgis/providers')
        self.app.initQgis()

    def tearDown(self):
        '''Tear down - destroy the QGIS app'''
        self.app.exitQgis()

    def test_load(self):
        """Test if we are able to load our plugin"""
        print 'Testing load'
        myParent = QWidget()
        myCanvas = QgsMapCanvas(myParent)
        myIface = QgisInterface(myCanvas)
        myStub = Riab(myIface)
        #myStub.run()


if __name__ == "__main__":
    unittest.main()
