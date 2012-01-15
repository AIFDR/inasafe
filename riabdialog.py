'''
Disaster risk assessment tool developed by AusAid - **GUI Dialog.**

Contact : ole.moller.nielsen@gmail.com

.. note:: This program is free software; you can redistribute it and/or modify
     it under the terms of the GNU General Public License as published by
     the Free Software Foundation; either version 2 of the License, or
     (at your option) any later version.

.. todo:: Check raster is single band

'''

__author__ = 'tim@linfiniti.com'
__version__ = '0.0.1'
__date__ = '10/01/2011'
__copyright__ = ('Copyright 2012, Australia Indonesia Facility for '
                 'Disaster Reduction')


from PyQt4 import QtGui, QtCore
from ui_riab import Ui_Riab
import os

# Check if a pydevpath.txt file exists in the plugin folder (you
# need to rename it from settings.txt.templ in the standard plugin
# distribution) and if it does, read the pydevd path from it and
# enable the debug flag to true. Please see:
# http://linfiniti.com/2011/12/remote-debugging-qgis-python-plugins-with-pydev/
# for notes on setting up the debugging environment.
ROOT = os.path.dirname(__file__)
PATH = os.path.abspath(os.path.join(ROOT, 'pydevpath.txt'))
DEBUG = False
if os.path.isfile(PATH):
    try:
        PYDEVD_PATH = file(PATH, 'rt').readline()
        DEBUG = True
        import sys
        sys.path.append(PYDEVD_PATH)
        from pydevd import *
        print 'Debugging is enabled.'
        #print sys.path
    except:
        #fail silently
        pass

from qgis.core import QGis, QgsMapLayer
from impactcalculator import ImpactCalculator


class RiabDialog(QtGui.QDialog):
    '''Dialog implementation class for the Risk In A Box plugin.'''

    def __init__(self, iface):
        '''Constructor for the dialog.

        This dialog will allow the user to select layers and scenario details
        and subsequently run their model.

        Args:
           iface - a Quantum GIS QGisAppInterface instance.
        Returns:
           not applicable
        Raises:
           no exceptions explicitly raised
        '''
        if DEBUG:
            # settrace()
            pass
        QtGui.QDialog.__init__(self)

        # Save reference to the QGIS interface
        self.iface = iface

        # Set up the user interface from Designer.
        self.ui = Ui_Riab()
        self.ui.setupUi(self)
        self.getLayers()
        self.setOkButtonStatus()

    def validate(self):
        '''Helper method to evaluate the current state of the dialog and
        determine if it is appropriate for the OK button to be enabled
        or not.

        .. note:: The enabled state of the OK button on the dialog will
           NOT be updated (set True or False) depending on the outcome of
           the UI readiness tests performed - **only** True or False
           will be returned by the function.

        Args:
           None.
        Returns:
           A two-tuple consisting of:

           * Boolean reflecting the results of the valudation tests.
           * A message indicating any reason why the validation may
             have failed.

           Example::

               flag,msg = self.ui.validate()

        Raises:
           no exceptions explicitly raised
        '''
        myHazardItem = self.ui.lstHazardLayers.currentItem()
        myExposureItem = self.ui.lstExposureLayers.currentItem()
        if not myHazardItem or not myExposureItem:
            myMessage = 'Please ensure both Hazard layer and ' + \
            'Exposure layer are set before clicking OK.'
            return (False, myMessage)

    def setOkButtonStatus(self):
        '''Helper function to set the ok button status if the
        form is valid and disable it if it is not.
        Args:
           None.
        Returns:
           None.
        Raises:
           no exceptions explicitly raised.'''
        myButton = self.ui.buttonBox.button(self.ui.buttonBox.Ok)
        myFlag, myMessage = self.validate()
        myButton.setEnabled(myFlag)
        self.ui.wvResults.setHtml(myMessage)

    def getLayers(self):
        '''Helper function to obtain a list of layers currently loaded in QGIS.

        On invocation, this method will populate lstHazardLayers and
        lstExposureLayers on the dialog with a list of available layers. Only
        **singleband raster** layers will be added to the hazard layer list,
        and only **point vector** layers will be added to the exposure layer
        list.

        Args:
           None.
        Returns:
           None
        Raises:
           no
        '''

        for i in range(len(self.iface.mapCanvas().layers())):
            myLayer = self.iface.mapCanvas().layer(i)
            '''
            .. todo:: check raster is single band
                      store uuid in user property of list widget for layers
            '''
            if myLayer.type() == QgsMapLayer.RasterLayer:
                myItem = QtGui.QListWidgetItem(myLayer.name())
                myItem.setData(QtCore.Qt.UserRole, myLayer.source())
                self.ui.lstHazardLayers.addItem(myItem)

            elif myLayer.type() == QgsMapLayer.VectorLayer and \
            myLayer.geometryType() == QGis.Point:
                myItem = QtGui.QListWidgetItem(myLayer.name())
                myItem.setData(QtCore.Qt.UserRole, myLayer.source())
                self.ui.lstExposureLayers.addItem(myItem)
            else:
                pass  # skip the layer

        return

    def accept(self):
        '''Execute analysis when ok button is clicked.'''
        #QtGui.QMessageBox.information(self, "Risk In A Box", "testing...")
        myCalculator = ImpactCalculator()
        myHazardItem = self.ui.lstHazardLayers.currentItem()
        myExposureItem = self.ui.lstExposureLayers.currentItem()
        if not myHazardItem or not myExposureItem():
            myMessage = 'Please ensure both Hazard layer and ' + \
            'Exposure layer are set before clicking OK.'
            self.ui.wvResults.setHtml(myMessage)
            return
        myHazardFileName = myHazardItem.data(QtCore.Qt.UserRole)
        myExposureFileName = myExposureItem.data(QtCore.Qt.UserRole)

        myCalculator.setHazardLayer(myHazardFileName)
        myCalculator.setExposureLayer(myExposureFileName)
        myCalculator.run()
