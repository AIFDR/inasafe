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
__version__ = '0.2.0'
__date__ = '10/01/2011'
__copyright__ = ('Copyright 2012, Australia Indonesia Facility for '
                 'Disaster Reduction')

import unittest
import sys
import os
import numpy

# Add PARENT directory to path to make test aware of other modules
pardir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(pardir)


from utilities_test import (getQgisTestApp, assertHashForFile)
from gui.riabmap import RiabMap
from PyQt4 import QtGui
from qgis.core import (QgsSymbol,
                       QgsMapLayerRegistry,
                       QgsRectangle)
from qgis.gui import QgsMapCanvasLayer
from utilities_test import (loadLayer, setJakartaGeoExtent)
from utilities import getTempDir
try:
    from pydevd import *
    print 'Remote debugging is enabled.'
    DEBUG = True
except Exception, e:
    print 'Debugging was disabled'

QGISAPP, CANVAS, IFACE, PARENT = getQgisTestApp()


class RiabDockTest(unittest.TestCase):
    """Test the risk in a box GUI"""
    def setUp(self):
        """Setup fixture run before each tests"""
        for myLayer in QgsMapLayerRegistry.instance().mapLayers():
            QgsMapLayerRegistry.instance().removeMapLayer(myLayer)

    def test_riabMap(self):
        """Test making a pdf using the RiabMap class."""
        myLayer, myType = loadLayer('test_shakeimpact.shp')
        del myType
        myCanvasLayer = QgsMapCanvasLayer(myLayer)
        CANVAS.setLayerSet([myCanvasLayer])
        myMap = RiabMap(IFACE)
        myRect = QgsRectangle(106.7894, -6.2308, 106.8004, -6.2264)
        CANVAS.setExtent(myRect)
        CANVAS.refresh()
        myMap.setImpactLayer(myLayer)
        myPath = os.path.join(getTempDir(), 'outCustom.pdf')
        if os.path.exists(myPath):
            os.remove(myPath)
        myMap.makePdf(myPath)
        assert os.path.exists(myPath)
        # ,, note:: Template writing is experimental
        myMap.writeTemplate(os.path.join(getTempDir(), 'template.qpt'))
        #os.remove(myPath)

    def test_getLegend(self):
        """Getting a legend for a generic layer works."""
        myLayer, myType = loadLayer('test_shakeimpact.shp')
        del myType
        myMap = RiabMap(IFACE)
        myMap.setImpactLayer(myLayer)
        assert myMap.layer is not None
        myLegend = myMap.getLegend()
        myPath = os.path.join(getTempDir(), 'getLegend.png')
        myLegend.save(myPath, 'PNG')
        myExpectedHash = '5e67f182a7e8f0d065c32cbebcef8561'
        assertHashForFile(myExpectedHash, myPath)

    def test_getVectorLegend(self):
        """Getting a legend for a vector layer works."""
        myLayer, myType = loadLayer('test_shakeimpact.shp')
        del myType
        myMap = RiabMap(IFACE)
        myMap.setImpactLayer(myLayer)
        myMap.getVectorLegend()
        myPath = os.path.join(getTempDir(), 'getVectorLegend.png')
        myMap.legend.save(myPath, 'PNG')
        myExpectedHash = '5e67f182a7e8f0d065c32cbebcef8561'
        assertHashForFile(myExpectedHash, myPath)

    def test_getRasterLegend(self):
        """Getting a legend for a raster layer works."""
        myLayer, myType = loadLayer('test_floodimpact.tif')
        del myType
        myMap = RiabMap(IFACE)
        myMap.setImpactLayer(myLayer)
        myMap.getRasterLegend()
        myPath = os.path.join(getTempDir(), 'getRasterLegend.png')
        myMap.legend.save(myPath, 'PNG')
        myExpectedHash = '1a47a474981fc1acfae8e751e5afe5f0'
        assertHashForFile(myExpectedHash, myPath)

    def addSymbolToLegend(self):
        """Test we can add a symbol to the legend."""
        myLayer, myType = loadLayer('test_floodimpact.tif')
        del myType
        myMap = RiabMap(IFACE)
        myMap.setImpactLayer(myLayer)
        myMap.legend = None
        mySymbol = QgsSymbol()
        mySymbol.setColor(QtGui.QColor(12, 34, 56))
        myMap.addSymbolToLegend(mySymbol,
                                theMin=0,
                                theMax=2,
                                theCategory=None,
                                theLabel='Foo')
        myPath = os.path.join(getTempDir(), 'addSymbolToLegend.png')
        myMap.legend.save(myPath, 'PNG')
        myExpectedHash = '1234'
        assertHashForFile(myExpectedHash, myPath)

    def test_addClassToLegend(self):
        """Test we can add a class to the map legend."""
        myLayer, myType = loadLayer('test_shakeimpact.shp')
        del myType
        myMap = RiabMap(IFACE)
        myMap.setImpactLayer(myLayer)
        myMap.legend = None
        myColour = QtGui.QColor(12, 34, 126)
        myMap.addClassToLegend(myColour,
                               theMin=None,
                               theMax=None,
                               theCategory='foo',
                               theLabel='bar')
        myMap.addClassToLegend(myColour,
                               theMin=None,
                               theMax=None,
                               theCategory='foo',
                               theLabel='foo')
        myPath = os.path.join(getTempDir(), 'addClassToLegend.png')
        myMap.legend.save(myPath, 'PNG')
        myExpectedHash = '5fe2c1748d974fbb49ddb513208e242b'
        assertHashForFile(myExpectedHash, myPath)

    def test_getMapTitle(self):
        """Getting the map title from the keywords"""
        myLayer, myType = loadLayer('test_floodimpact.tif')
        del myType
        myMap = RiabMap(IFACE)
        myMap.setImpactLayer(myLayer)
        myTitle = myMap.getMapTitle()
        myExpectedTitle = 'Penduduk yang Mungkin dievakuasi'
        myMessage = 'Expected: %s\nGot:\n %s' % (myExpectedTitle, myTitle)
        assert myTitle == myExpectedTitle, myMessage

    def Xtest_renderTable(self):
        """Test that html renders nicely. Commented out for now until we work
        out how to get webkit to do offscreen rendering nicely."""
        myFilename = 'test_floodimpact.tif'
        myLayer, myType = loadLayer(myFilename)
        CANVAS.refresh()
        del myType
        myMessage = 'Layer is not valid: %s' % myFilename
        assert myLayer.isValid(), myMessage
        myMap = RiabMap(IFACE)
        myMap.setImpactLayer(myLayer)
        myPixmap = myMap.renderImpactTable()
        assert myPixmap is not None
        myExpectedWidth = 500
        myExpectedHeight = 300
        myMessage = 'Invalid width - got %s expected %s' % (
                                    myPixmap.width(),
                                    myExpectedWidth)
        assert myPixmap.width() == myExpectedWidth, myMessage
        myMessage = 'Invalid height - got %s expected %s' % (
                                    myPixmap.height(),
                                    myExpectedHeight)
        assert myPixmap.height() == myExpectedHeight
        myPath = os.path.join(getTempDir(), 'renderImpactTable.png')
        myPixmap.save(myPath, 'PNG')
        myExpectedHash = 'c9164d5c2bb85c6081905456ab827f3e'
        assertHashForFile(myExpectedHash, myPath)

    def test_renderTemplate(self):
        """Test that load template works"""
        #Use the template from our resources bundle
        myInPath = ':/plugins/riab/basic.qpt'
        myLayer, myType = loadLayer('test_shakeimpact.shp')
        del myType

        myCanvasLayer = QgsMapCanvasLayer(myLayer)
        CANVAS.setLayerSet([myCanvasLayer])
        myMap = RiabMap(IFACE)
        setJakartaGeoExtent()
        myMap.setImpactLayer(myLayer)
        myOutPath = os.path.join(getTempDir(), 'outTemplate.pdf')
        if os.path.exists(myOutPath):
            os.remove(myOutPath)
        myMap.renderTemplate(myInPath, myOutPath)
        assert os.path.exists(myOutPath)
        #os.remove(myPath)

    def test_mmPointConversion(self):
        """Test that conversions between pixel and page dimensions work."""
        myMap = RiabMap(IFACE)
        myDpi = 300
        myMap.pageDpi = myDpi
        myPixels = 300
        myMM = 25.4  # 1 inch
        myResult = myMap.pointsToMM(myPixels)
        myMessage = "Expected: %s\nGot: %s" % (myMM, myResult)
        assert myResult == myMM, myMessage
        myResult = myMap.mmToPoints(myMM)
        myMessage = "Expected: %s\nGot: %s" % (myPixels, myResult)
        assert myResult == myPixels, myMessage

if __name__ == '__main__':
    suite = unittest.makeSuite(RiabDockTest, 'test')
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite)
