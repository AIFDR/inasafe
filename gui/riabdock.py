"""
Disaster risk assessment tool developed by AusAid - **GUI Dialog.**

Contact : ole.moller.nielsen@gmail.com

.. note:: This program is free software; you can redistribute it and/or modify
     it under the terms of the GNU General Public License as published by
     the Free Software Foundation; either version 2 of the License, or
     (at your option) any later version.

.. todo:: Check raster is single band

"""

__author__ = 'tim@linfiniti.com'
__version__ = '0.0.1'
__date__ = '10/01/2011'
__copyright__ = ('Copyright 2012, Australia Indonesia Facility for '
                 'Disaster Reduction')


from PyQt4 import QtGui, QtCore, QtWebKit
from PyQt4.QtWebKit import QWebSettings
from ui_riabdock import Ui_RiabDock
from riabhelp import RiabHelp
from utilities import get_exception_with_stacktrace
import sys
import os

# Check if a pydevpath.txt file exists in the plugin folder (you
# need to rename it from settings.txt.templ in the standard plugin
# distribution) and if it does, read the pydevd path from it and
# enable the debug flag to true. Please see:
# http://linfiniti.com/2011/12/remote-debugging-qgis-python-plugins-with-pydev/
# for notes on setting up the debugging environment.
ROOT = os.path.dirname(__file__)
PATH = os.path.abspath(os.path.join(ROOT, 'pydevpath.txt'))

if os.path.isfile(PATH):
    try:
        PYDEVD_PATH = file(PATH, 'rt').readline().strip()
        sys.path.append(PYDEVD_PATH)

        from pydevd import *
        print 'Debugging is enabled.'

        DEBUG = True
    except Exception, e:
        print 'Debugging was requested, but could no be enabled: %s' % str(e)

from qgis.core import (QGis, QgsMapLayer, QgsVectorLayer, QgsRasterLayer,
                       QgsMapLayerRegistry, QgsGraduatedSymbolRendererV2,
                       QgsSymbolV2, QgsRendererRangeV2, QgsRectangle,
                       QgsSymbolLayerV2Registry, QgsColorRampShader,
                       QgsCoordinateReferenceSystem,
                       QgsCoordinateTransform)
from qgis.gui import QgsMapCanvas
from impactcalculator import ImpactCalculator
from riabclipper import clipLayer
from impactcalculator import getOptimalExtent

import resources
# Helper functions


def setVectorStyle(qgisVectorLayer, style):
    """Set QGIS vector style based on RIAB style dictionary

    Input
        qgisVectorLayer: Qgis layer
        style: Dictionary of the form as in the example below

        {'target_field': 'DMGLEVEL',
        'style_classes':
        [{'opacity': 1, 'max': 1.5, 'colour': '#fecc5c',
          'min': 0.5, 'label': 'Low damage'},
        {'opacity': 1, 'max': 2.5, 'colour': '#fd8d3c',
         'min': 1.5, 'label': 'Medium damage'},
        {'opacity': 1, 'max': 3.5, 'colour': '#f31a1c',
         'min': 2.5, 'label': 'High damage'}]}

    Output
        Sets and saves style for qgisVectorLayer

    """

    myTargetField = style['target_field']
    myClasses = style['style_classes']
    myGeometryType = qgisVectorLayer.geometryType()

    myRangeList = []
    for myClass in myClasses:
        myOpacity = myClass['opacity']
        myMax = myClass['max']
        myMin = myClass['min']
        myColour = myClass['colour']
        myLabel = myClass['label']
        myColour = QtGui.QColor(myColour)
        mySymbol = QgsSymbolV2.defaultSymbol(myGeometryType)
        myColourString = "%s, %s, %s" % (
                         myColour.red(),
                         myColour.green(),
                         myColour.blue())
        # Work around for the fact that QgsSimpleMarkerSymbolLayerV2
        # python bindings are missing from the QGIS api.
        # .. see:: http://hub.qgis.org/issues/4848
        # We need to create a custom symbol layer as
        # the border colour of a symbol can not be set otherwise
        myRegistry = QgsSymbolLayerV2Registry.instance()
        if myGeometryType == QGis.Point:
            myMetadata = myRegistry.symbolLayerMetadata("SimpleMarker")
            # note that you can get a list of available layer properties
            # that you can set by doing e.g.
            # QgsSimpleMarkerSymbolLayerV2.properties()
            mySymbolLayer = myMetadata.createSymbolLayer({"color_border":
                                                          myColourString})
            mySymbol.changeSymbolLayer(0, mySymbolLayer)
        elif myGeometryType == QGis.Polygon:
            myMetadata = myRegistry.symbolLayerMetadata("SimpleFill")
            mySymbolLayer = myMetadata.createSymbolLayer({"color_border":
                                                          myColourString})
            mySymbol.changeSymbolLayer(0, mySymbolLayer)
        else:
            # for lines we do nothing special as the property setting
            # below should give us what we require.
            pass

        mySymbol.setColor(myColour)
        mySymbol.setAlpha(myOpacity)
        myRange = QgsRendererRangeV2(myMin,
                                     myMax,
                                     mySymbol,
                                     myLabel)
        myRangeList.append(myRange)

    myRenderer = QgsGraduatedSymbolRendererV2('', myRangeList)
    myRenderer.setMode(QgsGraduatedSymbolRendererV2.EqualInterval)
    myRenderer.setClassAttribute(myTargetField)
    qgisVectorLayer.setRendererV2(myRenderer)
    qgisVectorLayer.saveDefaultStyle()


def setRasterStyle(qgisRasterLayer, style):
    """Set QGIS raster style based on RIAB style dictionary

    Input
        qgisRasterLayer: Qgis layer
        style: Dictionary of the form as in the example below

        {
            'style_classes':
            [{'max': 1.5, 'colour': '#fecc5c', label': 'Low damage'},
             {'max': 3, 'colour': '#fd8d3c', label': 'Medium damage'},
             {'max': 5, 'colour': '#ffccgg', label': 'High damage'}
            ]
        }

    Output
        Sets and saves style for qgisRasterLayer

    """
    myClasses = style['style_classes']
    myRangeList = []
    for myClass in myClasses:
        myMax = myClass['max']
        myColour = myClass['colour']
        #myLabel = myClass['label']
        myShader = QgsColorRampShader.ColorRampItem(myMax, myColour)
        myRangeList.append(myShader)

    # Apply the shading algorithm and design their ramp
    qgisRasterLayer.setColorShadingAlgorithm(QgsRasterLayer.ColorRampShader)
    myFunction = qgisRasterLayer.rasterShader().rasterShaderFunction()
    myFunction.setColorRampType(QgsColorRampShader.DISCRETE)
    myFunction.setColorRampItemList(myRangeList)


class RiabDock(QtGui.QDockWidget):
    """Dock implementation class for the Risk In A Box plugin."""

    def __init__(self, iface, guiContext=True):
        """Constructor for the dialog.

        This dialog will allow the user to select layers and scenario details
        and subsequently run their model.

        Args:

           * iface - a Quantum GIS QGisAppInterface instance.
           * guidContext - an optional paramter, defaults to True. Set to
             False if you do not wish to see popup messages etc. Used
             mainly by init tests.

        Returns:
           not applicable
        Raises:
           no exceptions explicitly raised
        """
        QtGui.QDockWidget.__init__(self, None)

        # Save reference to the QGIS interface
        self.iface = iface
        self.header = None  # for storing html header template
        self.footer = None  # for storing html footer template
        self.suppressDialogsFlag = guiContext
        self.calculator = ImpactCalculator()
        self.runner = None
        self.helpDialog = None
        # Set up the user interface from Designer.
        self.ui = Ui_RiabDock()
        self.ui.setupUi(self)
        self.getLayers()
        self.setOkButtonStatus()

        myButton = self.ui.pbnHelp
        QtCore.QObject.connect(myButton, QtCore.SIGNAL('clicked()'),
                               self.showHelp)
        #self.showHelp()
        myButton = self.ui.pbnRunStop
        QtCore.QObject.connect(myButton, QtCore.SIGNAL('clicked()'),
                               self.accept)
        QtCore.QObject.connect(self.iface.mapCanvas(),
                               QtCore.SIGNAL('layersChanged()'),
                               self.getLayers)
        # update the functions list whenever we change the hazard
        QtCore.QObject.connect(self.ui.cboHazard,
                               QtCore.SIGNAL('currentIndexChanged(int)'),
                               self.getFunctions)
        # update the functions list whenever we change the exposure
        QtCore.QObject.connect(self.ui.cboExposure,
                               QtCore.SIGNAL('currentIndexChanged(int)'),
                               self.getFunctions)
        #myAttribute = QtWebKit.QWebSettings.DeveloperExtrasEnabled
        #QtWebKit.QWebSettings.setAttribute(myAttribute, True)

    def validate(self):
        """Helper method to evaluate the current state of the dialog and
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
        """
        myHazardIndex = self.ui.cboHazard.currentIndex()
        myExposureIndex = self.ui.cboExposure.currentIndex()
        if myHazardIndex == -1 or myExposureIndex == -1:
            myMessage = ('<span class="label notice">Getting started:</span> '
            'To use this tool you need to add some layers to your QGIS '
            'project. At least one <em>hazard</em> layer (e.g. earthquake MMI)'
            'and one <em>exposure</em> layer (e.g. dwellings) are available. '
            'When you are ready, click the <em>run</em> button below.')
            return (False, myMessage)
        else:
            return (True, '')

    def setOkButtonStatus(self):
        """Helper function to set the ok button status if the
        form is valid and disable it if it is not.
        Args:
           None.
        Returns:
           None.
        Raises:
           no exceptions explicitly raised."""
        myButton = self.ui.pbnRunStop
        myFlag, myMessage = self.validate()
        myButton.setEnabled(myFlag)
        if myMessage is not '':
            self.displayHtml(myMessage)

    def getLayers(self):
        """Helper function to obtain a list of layers currently loaded in QGIS.

        On invocation, this method will populate cboHazard and
        cboExposure on the dialog with a list of available layers. Only
        **singleband raster** layers will be added to the hazard layer list,
        and only **point vector** layers will be added to the exposure layer
        list.

        Args:
           None.
        Returns:
           None
        Raises:
           no
        """
        self.ui.cboHazard.clear()
        self.ui.cboExposure.clear()
        for i in range(len(self.iface.mapCanvas().layers())):

            myLayer = self.iface.mapCanvas().layer(i)
            """
            .. todo:: check raster is single band
            store uuid in user property of list widget for layers
            """

            myName = myLayer.name()
            mySource = str(myLayer.id())
            # find out if the layer is a hazard or an exposure
            # layer by querying its keywords. If the query fails,
            # the layer will be ignored.
            try:
                myCategory = self.calculator.getKeywordFromFile(
                                str(myLayer.source()), 'category')
            except:
                # continue ignoring this layer
                continue
            # See if there is a title for this layer, if not,
            # fallback to the layer's filename
            myTitle = None
            try:
                myTitle = self.calculator.getKeywordFromFile(
                            str(myLayer.source()), 'title')
            except:
                myTitle = myName

            if myCategory == 'hazard':
                self.ui.cboHazard.addItem(myTitle, mySource)
            elif myCategory == 'exposure':
                self.ui.cboExposure.addItem(myTitle, mySource)

        # now populate the functions list based on the layers loaded
        self.getFunctions()
        self.setOkButtonStatus()
        return

    def getFunctions(self):
        """Helper function to obtain a list of impact functions from
        the impact calculator.

        Args:
           None.
        Returns:
           None
        Raises:
           no
        """
        settrace()
        self.ui.cboFunction.clear()
        # get the keyword dicts for hazard and exposure
        myHazardLayer = self.getHazardLayer()
        if myHazardLayer is None:
            return
        myHazardFile = myHazardLayer.source()
        myExposureLayer = self.getExposureLayer()
        if myExposureLayer is None:
            return
        myExposureFile = myExposureLayer.source()
        myHazardKeywords = self.calculator.getKeywordFromFile(
                                            str(myHazardFile))
        myExposureKeywords = self.calculator.getKeywordFromFile(
                                            str(myExposureFile))

        # now find out which functions can be used with these layers
        myList = [myHazardKeywords, myExposureKeywords]
        try:
            myDict = self.calculator.availableFunctions(myList)
            #populate the hazard combo with the available functions
            for myFunction in myDict:  # use only key
                self.ui.cboFunction.addItem(myFunction)
        except Exception, e:
            raise e

    def readImpactLayer(self, engineImpactLayer):
        """Helper function to read and validate layer

        Args
            engineImpactLayer: Layer object as provided by the riab engine

        Returns
            validated qgis layer or None

        Raises
            Exception if layer is not valid
        """

        msg = ('Input argument must be a RIAB spatial object. '
               'I got %s' % type(engineImpactLayer))
        if not hasattr(engineImpactLayer, 'is_riab_spatial_object'):
            raise Exception(msg)
        if not engineImpactLayer.is_riab_spatial_object:
            raise Exception(msg)

        # Get associated filename and symbolic name
        myFilename = engineImpactLayer.get_filename()
        myName = engineImpactLayer.get_name()

        # Read layer
        if engineImpactLayer.is_vector:
            qgisLayer = QgsVectorLayer(myFilename, myName, 'ogr')
        elif engineImpactLayer.is_raster:
            qgisLayer = QgsRasterLayer(myFilename, myName)

        # Verify that new qgis layer is valid
        if qgisLayer.isValid():
            return qgisLayer
        else:
            msg = 'Loaded impact layer "%s" is not valid' % myFilename
            raise Exception(msg)

    def getHazardLayer(self):
        """Obtain qgsmaplayer id from the userrole of the QtCombo for exposure
        and return it as a QgsMapLayer"""
        myIndex = self.ui.cboHazard.currentIndex()
        if myIndex < 0:
            return None
        myLayerId = self.ui.cboHazard.itemData(myIndex,
                             QtCore.Qt.UserRole).toString()
        myLayer = QgsMapLayerRegistry.instance().mapLayer(myLayerId)
        return myLayer

    def getExposureLayer(self):
        """Obtain the name of the path to the exposure file from the
        userrole of the QtCombo for exposure."""
        myIndex = self.ui.cboExposure.currentIndex()
        if myIndex < 0:
            return None
        myLayerId = self.ui.cboExposure.itemData(myIndex,
                             QtCore.Qt.UserRole).toString()
        myLayer = QgsMapLayerRegistry.instance().mapLayer(myLayerId)
        return myLayer

    def accept(self):
        """Execute analysis when ok button is clicked."""
        self.showBusy()
        myFlag, myMessage = self.validate()
        if not myFlag:
            self.displayHtml(myMessage)
            self.hideBusy()
            return

        myHazardFilename = None
        myExposureFilename = None
        try:
            myHazardFilename, myExposureFilename = self.optimalClip()
        except Exception, e:
            QtGui.qApp.restoreOverrideCursor()
            self.hideBusy()
            msg = ('<p><span class="label important">Error:</span> '
                   'An exception occurred when creating layer '
                   'subsets clipped to the optimal extent: %s</p>' %
                   ((str(e))))
            msg += get_exception_with_stacktrace(e, html=True)
            self.displayHtml(msg)
            return

        self.calculator.setHazardLayer(myHazardFilename)
        self.calculator.setExposureLayer(myExposureFilename)
        self.calculator.setFunction(self.ui.cboFunction.currentText())

        # Start it in its own thread
        self.runner = self.calculator.getRunner()
        QtCore.QObject.connect(self.runner.notifier(),
                               QtCore.SIGNAL('done()'),
                               self.completed)
        #self.runner.start()  # Run in different thread
        try:
            QtGui.qApp.setOverrideCursor(
                    QtGui.QCursor(QtCore.Qt.WaitCursor))
            self.repaint()
            self.runner.run()  # Run in same thread
            QtGui.qApp.restoreOverrideCursor()
            # .. todo :: Disconnect done slot/signal
        except Exception, e:
            QtGui.qApp.restoreOverrideCursor()
            self.hideBusy()
            msg = 'An exception occurred when starting the model: %s' % (
                    (str(e)))
            self.displayHtml(msg)

    def completed(self):
        """Slot activated when the process is done."""

        # Try to run completion code
        try:
            myReport = self._completed()
        except Exception, e:
            # Display message and traceback
            msg = get_exception_with_stacktrace(e, html=True)
            self.displayHtml(msg)
        else:
            # On succes, display generated report
            self.displayHtml(myReport)

        # Hide hourglass
        self.hideBusy()

    def _completed(self):
        """Helper function for slot activated when the process is done.

        Args
            None
        Returns
            Report to render on canvas
        Raises
            Exceptions on a range of error conditions

        Provides report out from impact_function to canvas
        """

        myMessage = self.runner.result()
        engineImpactLayer = self.runner.impactLayer()

        if engineImpactLayer is None:
            msg = ('No impact layer was calculated. '
                   'Error message: %s\n' % str(myMessage))
            raise Exception(msg)

        # Get tabular information from impact layer
        myReport = self.calculator.getKeywordFromLayer(engineImpactLayer,
                                               'caption')

        # Get requested style for impact layer of either kind
        myStyle = engineImpactLayer.get_style_info()

        # Load impact layer into QGIS
        qgisImpactLayer = self.readImpactLayer(engineImpactLayer)

        # Determine styling for QGIS layer
        if engineImpactLayer.is_vector:
            if not myStyle:
                # Set default style if possible
                pass
            else:
                setVectorStyle(qgisImpactLayer, myStyle)
        elif engineImpactLayer.is_raster:
            if not myStyle:
                qgisImpactLayer.setDrawingStyle(
                                QgsRasterLayer.SingleBandPseudoColor)
                qgisImpactLayer.setColorShadingAlgorithm(
                                QgsRasterLayer.PseudoColorShader)
            else:
                setRasterStyle(qgisImpactLayer, myStyle)

        else:
            msg = ('Impact layer %s was neither a raster or a '
                   'vector layer' % qgisImpactLayer.source())
            raise Exception(msg)

        # Finally, add layer to QGIS
        QgsMapLayerRegistry.instance().addMapLayer(qgisImpactLayer)

        # Return text to display in report pane
        return myReport

    def showHelp(self):
        """Load the help text into the wvResults widget"""
        if not self.helpDialog:
            self.helpDialog = RiabHelp(self.iface.mainWindow())
        self.helpDialog.show()

    def showBusy(self):
        """A helper function to indicate the plugin is processing."""
        #self.ui.pbnRunStop.setText('Cancel')
        self.ui.pbnRunStop.setEnabled(False)
        myHtml = ('<div><span class="label success">'
                   'Analyzing this question...</span></div>'
                   '<div><img src="qrc:/plugins/riab/ajax-loader.gif" />'
                   '</div>')
        self.displayHtml(myHtml)
        self.repaint()
        self.ui.grpQuestion.setEnabled(False)

    def hideBusy(self):
        """A helper function to indicate processing is done."""
        #self.ui.pbnRunStop.setText('Run')
        if self.runner:
            del self.runner
            self.runner = None

        self.ui.grpQuestion.setEnabled(True)
        self.ui.pbnRunStop.setEnabled(True)
        self.repaint()

    def resetForm(self):
        """Reset the form contents to their onload state."""
        self.ui.cboFunction.setCurrentIndex(0)
        self.ui.cboHazard.setCurrentIndex(0)
        self.ui.cboExposure.setCurrentIndex(0)
        self.showHelp()

    def enableBusyCursor(self):
        """Set the hourglass enabled."""
        QtGui.qApp.setOverrideCursor(QtGui.QCursor(QtCore.Qt.WaitCursor))

    def disableBusyCursor(self):
        """Disable the hourglass cursor"""
        QtGui.qApp.restoreOverrideCursor()

    def optimalClip(self):
        """ A helper function to perform an optimal clip of the input data.
        Optimal extent should be considered as the intersection between
        the three inputs. The riab library will perform various checks
        to ensure that the extent is tenable, includes data from both
        etc.

        The result of this function will be two layers which are
        clipped if needed.

        Args:
            None
        Returns:
            A two-tuple containing the paths to the clipped hazard and
            exposure layers.

        Raises:
            Any exceptions raised by the RIAB library will be propogated.
        """
        myCanvas = self.iface.mapCanvas().extent()
        myHazardLayer = self.getHazardLayer()
        myExposureLayer = self.getExposureLayer()
        myRect = myCanvas.extent()
        # reproject the mapcanvas extent to EPSG:4326 if needed
        myDestinationCrs = QgsCoordinateReferenceSystem()
        myDestinationCrs.createFromEpsg(4326)
        myXForm = QgsCoordinateTransform(myCanvas.crs(),
                                         myDestinationCrs)

        # Get the clip area in the layer's crs
        myProjectedExtent = myXForm.transformBoundingBox(myRect)

        myExtent = [myProjectedExtent.xMinimum(),
                    myProjectedExtent.yMinimum(),
                    myProjectedExtent.xMaximum(),
                    myProjectedExtent.yMaximum()]

        #myGeoHazardLayer = reproject()

        try:
            myExtent = getOptimalExtent(myHazardLayer.source(),
                                    myExposureLayer.source(),
                                    myProjectedExtent)
        except Exception, e:
            msg = ('<p>There '
                   'was insufficient overlap between the input layers '
                   'and / or the layers and the viewport. Please select '
                   'two overlapping layers and zoom or pan to them. Full '
                   'details follow:</p>'
                   '<p>Failed to obtain the optimal extent given:</p>'
                   '<p>%s</p><p>%s</p>' %
                  (myHazardLayer.source(), myExposureLayer.source()))
            raise Exception(msg)
        myRect = QgsRectangle(myExtent[0],
                              myExtent[1],
                              myExtent[2],
                              myExtent[3])
        # Clip the vector to the bbox
        myClippedExposurePath = clipLayer(myExposureLayer, myRect)
        # Clip the vector to the bbox
        myClippedHazardPath = clipLayer(myHazardLayer, myRect)

        return (myClippedHazardPath, myClippedExposurePath)

    def htmlHeader(self):
        """Get a standard html header for wrapping content in."""
        if self.header is None:
            myFile = QtCore.QFile(':/plugins/riab/header.html')
            if not myFile.open(QtCore.QIODevice.ReadOnly):
                return '----'
            myStream = QtCore.QTextStream(myFile)
            self.header = myStream.readAll()
            myFile.close()
        return self.header

    def htmlFooter(self):
        """Get a standard html footer for wrapping content in."""
        if self.footer is None:
            myFile = QtCore.QFile(':/plugins/riab/footer.html')
            if not myFile.open(QtCore.QIODevice.ReadOnly):
                return '----'
            myStream = QtCore.QTextStream(myFile)
            self.footer = myStream.readAll()
            myFile.close()
        return self.footer

    def displayHtml(self, theMessage):
        """Given an html snippet, wrap it in a page header and footer
        and display it in the wvResults widget."""
        self.ui.wvResults.setHtml(self.htmlHeader() + theMessage +
                                self.htmlFooter())
