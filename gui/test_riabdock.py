"""
Disaster risk assessment tool developed by AusAid and World Bank
- **GUI Test Cases.**

Contact : ole.moller.nielsen@gmail.com

.. note:: This program is free software; you can redistribute it and/or modify
     it under the terms of the GNU General Public License as published by
     the Free Software Foundation; either version 2 of the License, or
     (at your option) any later version.

"""

__author__ = 'tim@linfiniti.com'
__version__ = '0.0.1'
__date__ = '10/01/2011'
__copyright__ = ('Copyright 2012, Australia Indonesia Facility for '
                 'Disaster Reduction')

import sys
import os
import unittest

from PyQt4 import QtGui, QtCore
from PyQt4.QtTest import QTest
from qgis.core import (QgsApplication,
                       QgsVectorLayer,
                       QgsRasterLayer,
                       QgsMapLayerRegistry)
from qgis.gui import QgsMapCanvas, QgsMapCanvasLayer
from qgisinterface import QgisInterface

from utilities import get_exception_with_stacktrace
from utilities_test import get_qgis_test_app, getUiState
from impactcalculator import ImpactCalculator
from gui.riabdock import RiabDock

# Get QGis app handle
qgis_app = get_qgis_test_app()

# Set form to test against
parent = QtGui.QWidget()
canvas = QgsMapCanvas(parent)
canvas.resize(QtCore.QSize(400, 400))
iface = QgisInterface(canvas)
myGuiContextFlag = False
form = RiabDock(iface, myGuiContextFlag)


def clearForm():
    """Helper function to  set all form elements to default state"""
    form.ui.cboHazard.clear()
    form.ui.cboExposure.clear()
    form.ui.cboFunction.setCurrentIndex(0)


def populateForm():
    """A helper function to populate the form and set it to a valid state."""
    loadLayers()
    form.ui.cboHazard.setCurrentIndex(0)
    form.ui.cboExposure.setCurrentIndex(0)
    #QTest.mouseClick(myHazardItem, Qt.LeftButton)
    #QTest.mouseClick(myExposureItem, Qt.LeftButton)


def loadLayers():
    """Helper function to load layers into the dialog."""

    # First unload any layers that may already be loaded
    for myLayer in QgsMapLayerRegistry.instance().mapLayers():
        QgsMapLayerRegistry.instance().removeMapLayer(myLayer)

    # Now go ahead and load our layers
    # FIXME (Ole): Use environment variable
    myRoot = os.path.abspath(os.path.join(
            os.path.dirname(__file__), '..'))
    myVectorPath = os.path.join(myRoot, 'riab_test_data',
                                'Padang_WGS84.shp')

    myPopulationRasterPath = os.path.join(myRoot, 'riab_test_data',
                                          'glp10ag.asc')
    myShakeRasterPath = os.path.join(myRoot, 'riab_test_data',
                                'Shakemap_Padang_2009.asc')
    myShakeFileInfo = QtCore.QFileInfo(myShakeRasterPath)
    myShakeBaseName = myShakeFileInfo.baseName()

    myPopulationFileInfo = QtCore.QFileInfo(myPopulationRasterPath)
    myPopulationBaseName = myPopulationFileInfo.baseName()

    # Create QGis Layer Instances
    myVectorLayer = QgsVectorLayer(myVectorPath, 'Padang Buildings', 'ogr')
    msg = 'Vector layer "%s" is not valid' % str(myVectorLayer.source())
    assert myVectorLayer.isValid(), msg

    myShakeRasterLayer = QgsRasterLayer(myShakeRasterPath, myShakeBaseName)
    msg = 'Raster layer "%s" is not valid' % str(myShakeRasterLayer.source())
    assert myShakeRasterLayer.isValid(), msg

    myPopulationRasterLayer = QgsRasterLayer(myPopulationRasterPath, myPopulationBaseName)
    msg = 'Raster layer "%s" is not valid' % str(myPopulationRasterLayer.source())
    assert myPopulationRasterLayer.isValid(), msg

    # Add layers to the registry (that QGis knows about)
    QgsMapLayerRegistry.instance().addMapLayer(myVectorLayer)
    QgsMapLayerRegistry.instance().addMapLayer(myShakeRasterLayer)
    QgsMapLayerRegistry.instance().addMapLayer(myPopulationRasterLayer)

    # Create Map Canvas Layer Instances
    myVectorCanvasLayer = QgsMapCanvasLayer(myVectorLayer)
    myShakeRasterCanvasLayer = QgsMapCanvasLayer(myShakeRasterLayer)
    myPopulationRasterCanvasLayer = QgsMapCanvasLayer(myPopulationRasterLayer)

    # Add MCL's to the canvas
    canvas.setLayerSet([myVectorCanvasLayer,
                        myShakeRasterCanvasLayer,
                        myPopulationRasterCanvasLayer])
    form.getLayers()


class RiabDockTest(unittest.TestCase):
    """Test the risk in a box GUI"""

    def test_defaults(self):
        """Test the GUI in its default state"""
        self.assertEqual(form.ui.cboHazard.currentIndex(), -1)
        self.assertEqual(form.ui.cboExposure.currentIndex(), -1)
        self.assertEqual(form.ui.cboFunction.currentIndex(), -1)

    def test_validate(self):
        """Validate function work as expected"""

        # First check that we DONT validate a clear form
        clearForm()
        myFlag, myMessage = form.validate()
        assert myMessage is not None, 'No reason for failure given'

        myMessage = 'Validation expected to fail on a cleared form.'
        self.assertEquals(myFlag, False, myMessage)

        # Now check we DO validate a populated form
        populateForm()
        myFlag = form.validate()
        myMessage = ('Validation expected to pass on' +
                     ' a populated for with selections.')
        assert(myFlag), myMessage

    def test_setOkButtonStatus(self):
        """OK button changes properly according to form validity"""

        # First check that we ok ISNT enabled on a clear form
        clearForm()
        myFlag, myMessage = form.validate()

        assert myMessage is not None, 'No reason for failure given'
        myMessage = 'Validation expected to fail on a cleared form.'
        self.assertEquals(myFlag, False, myMessage)

        # Now check OK IS enabled on a populated form
        populateForm()
        myFlag = form.validate()
        myMessage = ('Validation expected to pass on a ' +
                     'populated form with selections.')
        assert(myFlag), myMessage

    def test_run(self):
        """OK button works as expected"""

        # Push OK with the left mouse button
        clearForm()
        loadLayers()
        myOkWidget = form.ui.pbnRunStop

        msg = 'Run button was not enabled'
        assert form.ui.pbnRunStop.isEnabled(), msg

        D = getUiState(form.ui)

        #print D
        assert D == {'Hazard': 'Shakemap_Padang_2009',
                     'Exposure': 'Padang Buildings',
                     'Impact Function': 'Earthquake Guidelines Function',
                     'Run Button Enabled': True}

        QTest.mouseClick(myOkWidget, QtCore.Qt.LeftButton)

        #QTest.keyClicks(
        #  form.ui.buttonBox.button(form.ui.buttonBox.Cancel), " ")

    def test_loadLayers(self):
        """Layers can be loaded and list widget was updated appropriately
        """

        clearForm()
        loadLayers()
        msg = 'Expect 1 layer in hazard list widget but got %s' % \
              form.ui.cboHazard.count()
        self.assertEqual(form.ui.cboHazard.count(), 1), msg

        msg = 'Expect 1 layer in exposure list widget but got %s' % \
              form.ui.cboExposure.count()
        self.assertEqual(form.ui.cboExposure.count(), 2), msg


if __name__ == '__main__':
    unittest.main()
