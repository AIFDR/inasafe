"""
Disaster risk assessment tool developed by AusAid -
  **RIAB map making module.**

Contact : ole.moller.nielsen@gmail.com

.. note:: This program is free software; you can redistribute it and/or modify
     it under the terms of the GNU General Public License as published by
     the Free Software Foundation; either version 2 of the License, or
     (at your option) any later version.

"""

__author__ = 'tim@linfiniti.com'
__version__ = '0.2.0'
__date__ = '10/01/2011'
__copyright__ = 'Copyright 2012, Australia Indonesia Facility for '
__copyright__ += 'Disaster Reduction'

from qgis.core import (QgsComposition,
                       QgsComposerMap,
                       QgsComposerLabel,
                       QgsComposerPicture,
                       QgsComposerScaleBar,
                       QgsComposerShape,
                       QgsMapLayer,
                       QgsDistanceArea,
                       QgsPoint,
                       QgsRectangle)
from qgis.gui import QgsComposerView
import utilities
from riabexceptions import LegendLayerException
from PyQt4 import QtCore, QtGui, QtWebKit, QtXml
from impactcalculator import getKeywordFromFile
# Don't remove this even if it is flagged as unused by your ide
# it is needed for qrc:/ url resolution. See Qt Resources docs.
import resources
try:
    from pydevd import *
    print 'Remote debugging is enabled.'
    DEBUG = True
except Exception, e:
    print 'Debugging was disabled'


class RiabMap():
    """A class for creating a map."""
    def __init__(self, theIface):
        """Constructor for the RiabMap class.
        Args:
            theIface - reference to the QGIS iface object
        Returns:
            None
        Raises:
            Any exceptions raised by the RIAB library will be propogated.
        """
        self.iface = theIface
        self.layer = theIface.activeLayer()
        self.legend = None
        self.header = None
        self.footer = None
        # how high each row of the legend should be
        self.legendIncrement = 30
        self.pageWidth = 210  # width in mm
        self.pageHeight = 297  # height in mm
        self.pageDpi = 150.0
        self.pageMargin = 10  # margin in mm
        self.verticalSpacing = 1  # vertical spacing between elements
        self.showFramesFlag = False  # intended for debugging use only
        # make a square map where width = height = page width
        self.mapHeight = self.pageWidth - (self.pageMargin * 2)
        self.mapWidth = self.mapHeight
        self.disclaimer = self.tr('S.A.F.E. has been jointly developed by'
                                  ' BNPD, AusAid & the World Bank')

    def tr(self, theString):
        """We implement this ourself since we do not inherit QObject.

        Args:
           theString - string for translation.
        Returns:
           Translated version of theString.
        Raises:
           no exceptions explicitly raised.
        """
        return QtCore.QCoreApplication.translate('RiabMap', theString)

    def setImpactLayer(self, theLayer):
        """Mutator for the impact layer that will be used for stats,
        legend and reporting.
        Args:
            theLayer - a valid QgsMapLayer
        Returns:
            None
        Raises:
            Any exceptions raised by the RIAB library will be propogated.
        """
        self.layer = theLayer

    def renderTemplate(self, theTemplateFilePath, theOutputFilePath):
        """Load a QgsComposer map from a template and render it

        .. note:: THIS METHOD IS EXPERIMENTAL AND CURRENTLY NON FUNCTIONAL

        Args:
            theTemplateFilePath - path to the template that should be loaded.
            theOutputFilePath - path for the output pdf
        Returns:
            None
        Raises:
            None
        """
        self.setupComposition()
        self.setupPrinter(theOutputFilePath)
        if self.composition:
            myFile = QtCore.QFile(theTemplateFilePath)
            myDocument = QtXml.QDomDocument()
            myDocument.setContent(myFile, False)  # .. todo:: fix magic param
            myNodeList = myDocument.elementsByTagName('Composer')
            if myNodeList.size() > 0:
                myElement = myNodeList.at(0).toElement()
                self.composition.readXML(myElement, myDocument)
        self.renderPrintout()

    def getLegend(self):
        """Examine the classes of the impact layer associated with this print
        job.

        .. note: This is a wrapper for the rasterLegend and vectorLegend
           methods.
        Args:
            None
        Returns:
            None
        Raises:
            An InvalidLegendLayer will be raised if a legend cannot be
            created from the layer.
        """
        if self.layer is None:
            myMessage = self.tr('Unable to make a legend when map generator '
                                'has no layer set.')
            raise LegendLayerException(myMessage)
        try:
            getKeywordFromFile(str(self.layer.source()), 'impact_summary')
        except Exception, e:
            myMessage = self.tr('This layer does not appear to be an impact '
                                'layer. Try selecting an impact layer in the '
                                'QGIS layers list or creating a new impact '
                                'scenario before using the print tool.'
                                '\nMessage: %s' % str(e))
            raise Exception(myMessage)
        if self.layer.type() == QgsMapLayer.VectorLayer:
            return self.getVectorLegend()
        else:
            return self.getRasterLegend()
        return self.legend

    def getVectorLegend(self):
        """
        Args:
            None
        Returns:
            None
        Raises:
            An InvalidLegendLayer will be raised if a legend cannot be
            created from the layer.
        """
        if not self.layer.isUsingRendererV2():
            myMessage = self.tr('A legend can only be generated for '
                                'vector layers that use the "new symbology" '
                                'implementation in QGIS.')
            raise LegendLayerException(myMessage)
        # new symbology - subclass of QgsFeatureRendererV2 class
        self.legend = None
        myRenderer = self.layer.rendererV2()
        myType = myRenderer.type()
        if myType == "singleSymbol":
            mySymbol = myRenderer.symbol()
            self.addSymbolToLegend(theLabel=self.layer.name(),
                                   theSymbol=mySymbol)
        elif myType == "categorizedSymbol":
            for myCategory in myRenderer.categories():
                mySymbol = myCategory.symbol()
                self.addSymbolToLegend(
                                myCategory=myCategory.value().toString(),
                                theLabel=myCategory.label(),
                                theSymbol=mySymbol)
        elif myType == "graduatedSymbol":
            for myRange in myRenderer.ranges():
                mySymbol = myRange.symbol()
                self.addSymbolToLegend(theMin=myRange.lowerValue(),
                                       theMax=myRange.upperValue(),
                                       theLabel=myRange.label(),
                                       theSymbol=mySymbol)
        else:
            #type unknown
            myMessage = self.tr('Unrecognised renderer type found for the '
                                'impact layer. Please use one of these: '
                                'single symbol, categorised symbol or '
                                'graduated symbol and then try again.')
            raise LegendLayerException(myMessage)
        return self.legend

    def getRasterLegend(self):
        """
        Args:
            None
        Returns:
            None
        Raises:
            An InvalidLegendLayer will be raised if a legend cannot be
            created from the layer.
        """
        myShader = self.layer.rasterShader().rasterShaderFunction()
        myRampItems = myShader.colorRampItemList()
        myLastValue = 0  # Making an assumption here...
        print 'Source: %s' % self.layer.source()
        for myItem in myRampItems:
            myValue = myItem.value
            myLabel = myItem.label
            myColor = myItem.color
            print 'Value: %s Label %s' % (myValue, myLabel)
            self.addClassToLegend(myColor,
                      theMin=myLastValue,
                      theMax=myValue,
                      theLabel=myLabel)
            myLastValue = myValue
        return self.legend

    def addSymbolToLegend(self,
                         theSymbol,
                         theMin=None,
                         theMax=None,
                         theCategory=None,
                         theLabel=None):
        """Add a class to the current legend. If the legend is not defined,
        a new one will be created. A legend is just an image file with nicely
        rendered classes in it.

        .. note:: This method just extracts the colour from the symbol and then
           delegates to the addClassToLegend function.

        Args:

            * theSymbol - **Required** symbol for the class as a QgsSymbol
            * theMin - Optional minimum value for the class
            * theMax - Optional maximum value for the class\
            * theCategory - Optional category name (will be used in lieu of
                       min/max)
            * theLabel - Optional text label for the class

        Returns:
            None
        Raises:
            Throws an exception if the class could not be added for
            some reason..
        """
        myColour = theSymbol.color()
        self.addClassToLegend(myColour,
                              theMin=theMin,
                              theMax=theMax,
                              theLabel=theLabel)

    def addClassToLegend(self,
                         theColour,
                         theMin=None,
                         theMax=None,
                         theCategory=None,
                         theLabel=None):
        """Add a class to the current legend. If the legend is not defined,
        a new one will be created. A legend is just an image file with nicely
        rendered classes in it.

        Args:

            * theColour - **Required** colour for the class as a QColor
            * theMin - Optional minimum value for the class
            * theMax - Optional maximum value for the class\
            * theCategory - Optional category name (will be used in lieu of
                       min/max)
            * theLabel - Optional text label for the class

        Returns:
            None
        Raises:
            Throws an exception if the class could not be added for
            some reason..
        """
        self.extendLegend()
        myOffset = self.legend.height() - self.legendIncrement
        myPainter = QtGui.QPainter(self.legend)
        myBrush = QtGui.QBrush(theColour)
        myPainter.setBrush(myBrush)
        myPainter.setPen(theColour)
        myWhitespace = 0  # white space above and below each class itcon
        mySquareSize = self.legendIncrement - (myWhitespace * 2)
        myLeftIndent = 10
        myPainter.drawRect(QtCore.QRectF(myLeftIndent,
                                         myOffset + myWhitespace,
                                         mySquareSize, mySquareSize))
        myPainter.setPen(QtGui.QColor(0, 0, 0))  # outline colour
        myLabelX = myLeftIndent + mySquareSize + 10
        myPainter.drawText(myLabelX, myOffset + 25, theLabel)

    def extendLegend(self):
        """Grow the legend pixmap enough to accommodate one more legend entry.
        Args:
            None
        Returns:
            None
        Raises:
            Any exceptions raised by the RIAB library will be propogated.
        """
        if self.legend is None:
            self.legend = QtGui.QPixmap(300, 80)
            self.legend.fill(QtGui.QColor(255, 255, 255))
            myPainter = QtGui.QPainter(self.legend)
            myFontSize = 12
            myFontWeight = QtGui.QFont.Bold
            myItalicsFlag = False
            myFont = QtGui.QFont('verdana',
                             myFontSize,
                             myFontWeight,
                             myItalicsFlag)
            myPainter.setFont(myFont)
            myPainter.drawText(10, 25, self.tr('Legend'))
        else:
            # extend the existing legend down for the next class
            myPixmap = QtGui.QPixmap(300, self.legend.height() +
                                          self.legendIncrement)
            myPixmap.fill(QtGui.QColor(255, 255, 255))
            myPainter = QtGui.QPainter(myPixmap)

            myRect = QtCore.QRectF(0, 0,
                                   self.legend.width(),
                                   self.legend.height())
            myPainter.drawPixmap(myRect, self.legend, myRect)
            self.legend = myPixmap

    def setupComposition(self):
        """Set up the composition ready for drawing elements onto it.
        Args:
            None
        Returns:
            None
        Raises:
            None
        """
        myCanvas = self.iface.mapCanvas()
        myRenderer = myCanvas.mapRenderer()
        self.composition = QgsComposition(myRenderer)
        self.composition.setPlotStyle(QgsComposition.Print)
        self.composition.setPaperSize(self.pageWidth, self.pageHeight)
        self.composition.setPrintResolution(self.pageDpi)

    def setupPrinter(self, theFilename):
        """Create a QPrinter instance set up to print to an A4 portrait pdf

        Args:
            theFilename - filename for pdf generated using this printer
        Returns:
            None
        Raises:
            None
        """
        #
        # Create a printer device (we are 'printing' to a pdf
        #
        self.printer = QtGui.QPrinter()
        self.printer.setOutputFormat(QtGui.QPrinter.PdfFormat)
        self.printer.setOutputFileName(theFilename)
        self.printer.setPaperSize(QtCore.QSizeF(self.pageWidth,
                                             self.pageHeight),
                                             QtGui.QPrinter.Millimeter)
        self.printer.setFullPage(True)
        self.printer.setColorMode(QtGui.QPrinter.Color)
        myResolution = self.composition.printResolution()
        self.printer.setResolution(myResolution)

    def renderPrintout(self):
        """Generate the printout for our final map composition.
        Args:
            None
        Returns:
            None
        Raises:
            None
        """
        myPainter = QtGui.QPainter(self.printer)
        myPaperRectMM = self.printer.pageRect(QtGui.QPrinter.Millimeter)
        myPaperRectPx = self.printer.pageRect(QtGui.QPrinter.DevicePixel)
        self.composition.render(myPainter, myPaperRectPx, myPaperRectMM)
        myPainter.end()

    def drawLogo(self, theTopOffset):
        """Add a picture containing the logo to the map top left corner
        Args:
            theTopOffset - vertical offset at which the logo shoudl be drawn
        Returns:
            None
        Raises:
            None
        """
        myLogo = QgsComposerPicture(self.composition)
        myLogo.setPictureFile(':/plugins/riab/bnpb_logo.png')
        myLogo.setItemPosition(self.pageMargin,
                                   theTopOffset,
                                   10,
                                   10)
        myLogo.setFrame(self.showFramesFlag)
        myLogo.setZValue(1)  # To ensure it overlays graticule markers
        self.composition.addItem(myLogo)

    def drawTitle(self, theTopOffset):
        """Add a title to the composition
        Args:
            theTopOffset - vertical offset at which the map should be drawn
        Returns:
            float - the height of the label as rendered
        Raises:
            None
        """
        myFontSize = 14
        myFontWeight = QtGui.QFont.Bold
        myItalicsFlag = False
        myFont = QtGui.QFont('verdana',
                             myFontSize,
                             myFontWeight,
                             myItalicsFlag)
        myLabel = QgsComposerLabel(self.composition)
        myLabel.setFont(myFont)
        myHeading = self.tr('S.A.F.E. - Scenario Assement For Emergencies')
        myLabel.setText(myHeading)
        myLabel.adjustSizeToText()
        myLabelHeight = 10.0  # determined using qgis map composer
        myLabelWidth = 131.412   # item - position and size...option
        myLeftOffset = self.pageWidth - self.pageMargin - myLabelWidth
        myLabel.setItemPosition(myLeftOffset,
                                theTopOffset - 2,  # -2 to push it up a little
                                myLabelWidth,
                                myLabelHeight,
                                )
        myLabel.setFrame(self.showFramesFlag)
        self.composition.addItem(myLabel)
        return myLabelHeight

    def drawMap(self, theTopOffset):
        """Add a map to the composition and return the compsermap instance
        Args:
            theTopOffset - vertical offset at which the map should be drawn
        Returns:
            A QgsComposerMap instance is returned
        Raises:
            None
        """
        myMapWidth = self.mapWidth
        myComposerMap = QgsComposerMap(self.composition,
                                       self.pageMargin,
                                       theTopOffset,
                                       myMapWidth,
                                       self.mapHeight)
        #myExtent = self.iface.mapCanvas().extent()
        # The dimensions of the map canvas and the print compser map may
        # differ. So we set the map composer extent using the canvas and
        # then defer to the map canvas's map extents thereafter
        # Update: disabled as it results in a rectangular rather than
        # square map
        #myComposerMap.setNewExtent(myExtent)
        myComposerExtent = myComposerMap.extent()
        # Recenter the composer map on the center of the canvas
        # Note that since the composer map is square and the canvas may be
        # arbitrarily shaped, we center based on the longest edge
        myCanvasExtent = self.iface.mapCanvas().extent()
        myWidth = myCanvasExtent.width()
        myHeight = myCanvasExtent.height()
        myLongestLength = myWidth
        if myWidth < myHeight:
            myLongestLength = myHeight
        myHalfLength = myLongestLength / 2
        myCenter = myCanvasExtent.center()
        myMinX = myCenter.x() - myHalfLength
        myMaxX = myCenter.x() + myHalfLength
        myMinY = myCenter.y() - myHalfLength
        myMaxY = myCenter.y() + myHalfLength
        mySquareExtent = QgsRectangle(myMinX, myMinY, myMaxX, myMaxY)
        myComposerMap.setNewExtent(mySquareExtent)

        myComposerMap.setGridEnabled(True)
        myNumberOfSplits = 5
        # .. todo:: Write logic to adjust preciosn so that adjacent tick marks
        #    always have different displayed values
        myPrecision = 2
        myXInterval = myComposerExtent.width() / myNumberOfSplits
        myComposerMap.setGridIntervalX(myXInterval)
        myYInterval = myComposerExtent.height() / myNumberOfSplits
        myComposerMap.setGridIntervalY(myYInterval)
        myComposerMap.setGridStyle(QgsComposerMap.Cross)
        myCrossLengthMM = 1
        myComposerMap.setCrossLength(myCrossLengthMM)
        myComposerMap.setZValue(0)  # To ensure it does not overlay logo
        myFontSize = 6
        myFontWeight = QtGui.QFont.Normal
        myItalicsFlag = False
        myFont = QtGui.QFont('verdana',
                             myFontSize,
                             myFontWeight,
                             myItalicsFlag)
        myComposerMap.setGridAnnotationFont(myFont)
        myComposerMap.setGridAnnotationPrecision(myPrecision)
        myComposerMap.setShowGridAnnotation(True)
        myComposerMap.setGridAnnotationDirection(
                                        QgsComposerMap.BoundaryDirection)
        self.composition.addItem(myComposerMap)
        self.drawGraticuleMask(theTopOffset)
        return myComposerMap

    def drawGraticuleMask(self, theTopOffset):
        """A helper funtion to mask out graticule labels on the right side
           by overpainting a white rectangle on them.
        Args:
            theTopOffset - vertical offset at which the map should be drawn
        Returns:
            None
        Raises:
            None
        """
        myLeftOffset = self.pageMargin + self.mapWidth
        myRect = QgsComposerShape(myLeftOffset + 0.5,
                                  theTopOffset,
                                  self.pageWidth - myLeftOffset,
                                  self.mapHeight,
                                  self.composition)

        myRect.setShapeType(QgsComposerShape.Rectangle)
        # .. note:: Using -1 abuses the Qt api but QGIS refuses to hide border
        myRect.setLineWidth(-1)
        myRect.setFrame(False)
        myBrush = QtGui.QBrush(QtGui.QColor(255, 255, 255))
        # workaround for missing setTransparentFill missing from python api
        myRect.setBrush(myBrush)
        self.composition.addItem(myRect)

    def drawNativeScaleBar(self, theComposerMap, theTopOffset):
        """Draw a scale bar using QGIS' native drawing - in the case of
        geographic maps, scale will be in degrees, not km.
        Args:
            None
        Returns:
            None
        Raises:
            Any exceptions raised by the RIAB library will be propogated.
        """
        myScaleBar = QgsComposerScaleBar(self.composition)
        myScaleBar.setStyle('Numeric')  # optionally modify the style
        myScaleBar.setComposerMap(theComposerMap)
        myScaleBar.applyDefaultSize()
        myScaleBarHeight = myScaleBar.boundingRect().height()
        myScaleBarWidth = myScaleBar.boundingRect().width()
        # -1 to avoid overlapping the map border
        myScaleBar.setItemPosition(self.pageMargin + 1,
                                   theTopOffset + self.mapHeight -
                                     (myScaleBarHeight * 2),
                                   myScaleBarWidth,
                                   myScaleBarHeight)
        myScaleBar.setFrame(self.showFramesFlag)
        # Disabled for now
        #self.composition.addItem(myScaleBar)

    def drawScaleBar(self, theComposerMap, theTopOffset):
        """Add a numeric scale to the bottom left of the map

        We draw the scale bar manually because QGIS does not yet support
        rendering a scalebar for a geographic map in km.

        .. seealso:: :meth:`drawNativeScaleBar`

        Args:
            * theComposerMap - QgsComposerMap instance used as the basis
              scale calculations.
            * theTopOffset - vertical offset at which the map should be drawn
        Returns:
            None
        Raises:
            Any exceptions raised by the RIAB library will be propogated.
        """
        myCanvas = self.iface.mapCanvas()
        myRenderer = myCanvas.mapRenderer()
        #
        # Add a linear map scale
        #
        myDistanceArea = QgsDistanceArea()
        myDistanceArea.setSourceCrs(myRenderer.destinationCrs().srsid())
        myDistanceArea.setProjectionsEnabled(True)
        # Determine how wide our map is in km/m
        # Starting point at BL corner
        myComposerExtent = theComposerMap.extent()
        myStartPoint = QgsPoint(myComposerExtent.xMinimum(),
                                myComposerExtent.yMinimum())
        # Ending point at BR corner
        myEndPoint = QgsPoint(myComposerExtent.xMaximum(),
                              myComposerExtent.yMinimum())
        myGroundDistance = myDistanceArea.measureLine(myStartPoint, myEndPoint)
        # Get the equivalent map distance per page mm
        myMapWidth = self.mapWidth
        # How far is 1mm on map on the ground in meters?
        myMMToGroundDistance = myGroundDistance / myMapWidth
        #print 'MM:', myMMDistance
        # How long we want the scale bar to be in relation to the map
        myScaleBarToMapRatio = 0.5
        # How many divisions the scale bar should have
        myTickCount = 5
        myScaleBarWidthMM = myMapWidth * myScaleBarToMapRatio
        myPrintSegmentWidthMM = myScaleBarWidthMM / myTickCount
        # Segment width in real world (m)
        # We apply some logic here so that segments are displayed in meters
        # if each segment is less that 1000m otherwise km. Also the segment
        # lengths are rounded down to human looking numbers e.g. 1km not 1.1km
        myUnits = ''
        myGroundSegmentWidth = myPrintSegmentWidthMM * myMMToGroundDistance
        if myGroundSegmentWidth < 1000:
            myUnits = 'm'
            myGroundSegmentWidth = round(myGroundSegmentWidth)
            # adjust the segment width now to account for rounding
            myPrintSegmentWidthMM = myGroundSegmentWidth / myMMToGroundDistance
        else:
            myUnits = 'km'
            # Segment with in real world (km)
            myGroundSegmentWidth = round(myGroundSegmentWidth / 1000)
            myPrintSegmentWidthMM = ((myGroundSegmentWidth * 1000) /
                                    myMMToGroundDistance)
        # Now adjust the scalebar width to account for rounding
        myScaleBarWidthMM = myTickCount * myPrintSegmentWidthMM

        #print "SBWMM:", myScaleBarWidthMM
        #print "SWMM:", myPrintSegmentWidthMM
        #print "SWM:", myGroundSegmentWidthM
        #print "SWKM:", myGroundSegmentWidthKM
        # start drawing in line segments
        myScaleBarHeight = 5  # mm
        myLineWidth = 0.3  # mm
        myInsetDistance = 7  # how much to inset the scalebar into the map by
        myScaleBarX = self.pageMargin + myInsetDistance
        myScaleBarY = (theTopOffset + self.mapHeight -
                      myInsetDistance - myScaleBarHeight)  # mm

        # Draw an outer background box - shamelessly hardcoded buffer
        myRect = QgsComposerShape(myScaleBarX - 4,  # left edge
                                  myScaleBarY - 3,  # top edge
                                  myScaleBarWidthMM + 13,  # right edge
                                  myScaleBarHeight + 6,  # bottom edge
                                  self.composition)

        myRect.setShapeType(QgsComposerShape.Rectangle)
        myRect.setLineWidth(myLineWidth)
        myRect.setFrame(False)
        myBrush = QtGui.QBrush(QtGui.QColor(255, 255, 255))
        # workaround for missing setTransparentFill missing from python api
        myRect.setBrush(myBrush)
        self.composition.addItem(myRect)
        # Set up the tick label font
        myFontWeight = QtGui.QFont.Normal
        myFontSize = 6
        myItalicsFlag = False
        myFont = QtGui.QFont('verdana',
                             myFontSize,
                             myFontWeight,
                             myItalicsFlag)
        # Draw the bottom line
        myRect = QgsComposerShape(myScaleBarX,
                                  myScaleBarY + myScaleBarHeight,
                                  myScaleBarWidthMM,
                                  0.1,
                                  self.composition)

        myRect.setShapeType(QgsComposerShape.Rectangle)
        myRect.setLineWidth(myLineWidth)
        myRect.setFrame(False)
        self.composition.addItem(myRect)

        # Now draw the scalebar ticks
        for myTickCountIterator in range(0, myTickCount + 1):
            myDistanceSuffix = ''
            if myTickCountIterator == myTickCount:
                myDistanceSuffix = ' ' + myUnits
            myRealWorldDistance = ('%.0f%s' %
                                   (myTickCountIterator *
                                    myGroundSegmentWidth,
                                    myDistanceSuffix))
            #print 'RW:', myRealWorldDistance
            myMMOffset = myScaleBarX + (myTickCountIterator *
                                        myPrintSegmentWidthMM)
            #print 'MM:', myMMOffset
            myTickHeight = myScaleBarHeight / 2
            # Lines are not exposed by the api yet so we
            # bodge drawing lines using rectangles with 1px height or width
            myTickWidth = 0.1  # width or rectangle to be drawn
            myUpTickLine = QgsComposerShape(myMMOffset,
                                myScaleBarY + myScaleBarHeight - myTickHeight,
                                myTickWidth,
                                myTickHeight,
                                self.composition)

            myUpTickLine.setShapeType(QgsComposerShape.Rectangle)
            myUpTickLine.setLineWidth(myLineWidth)
            myUpTickLine.setFrame(False)
            self.composition.addItem(myUpTickLine)
            #
            # Add a tick label
            #
            myLabel = QgsComposerLabel(self.composition)
            myLabel.setFont(myFont)
            myLabel.setText(myRealWorldDistance)
            myLabel.adjustSizeToText()
            myLabel.setItemPosition(myMMOffset - 3,
                                myScaleBarY - myTickHeight)
            myLabel.setFrame(self.showFramesFlag)
            self.composition.addItem(myLabel)

    def drawImpactTitle(self, theTopOffset):
        """Draw the map subtitle - obtained from the impact layer keywords.
        Args:
            theTopOffset - vertical offset at which to begin drawing
        Returns:
            float - the height of the label as rendered
        Raises:
            None
        """
        myTitle = self.getMapTitle()
        if myTitle is not None:
            myFontSize = 20
            myFontWeight = QtGui.QFont.Bold
            myItalicsFlag = False
            myFont = QtGui.QFont('verdana',
                             myFontSize,
                             myFontWeight,
                             myItalicsFlag)
            myLabel = QgsComposerLabel(self.composition)
            myLabel.setFont(myFont)
            myHeading = myTitle
            myLabel.setText(myHeading)
            myLabel.adjustSizeToText()
            myLabelHeight = 12
            myLabel.setItemPosition(self.pageMargin,
                                theTopOffset,
                                self.mapHeight,
                                myLabelHeight,
                                )
            myLabel.setFrame(self.showFramesFlag)
            self.composition.addItem(myLabel)
            return myLabelHeight
        else:
            return None

    def drawLegend(self, theTopOffset):
        """Add a legend to the map using our custom legend renderer
        .. note:: getLegend generates a pixmap in 150dpi so if you set
           the map to a higher dpi it will appear undersized
        Args:
            theTopOffset - vertical offset at which to begin drawing
        Returns:
            None
        Raises:
            None
        """
        myPicture1 = QgsComposerPicture(self.composition)
        self.getLegend()
        myLegendFile = '/tmp/legend.png'
        self.legend.save(myLegendFile, 'PNG')
        myPicture1.setPictureFile(myLegendFile)
        myLegendHeight = self.pointsToMM(self.legend.height(), self.pageDpi)
        myLegendWidth = self.pointsToMM(self.legend.width(), self.pageDpi)
        myPicture1.setItemPosition(self.pageMargin,
                                   theTopOffset,
                                   myLegendWidth,
                                   myLegendHeight)
        myPicture1.setFrame(False)
        self.composition.addItem(myPicture1)

    def drawImpactSummary(self, theTopOffset):
        """Render the impact summary
        Args:
            theTopOffset - vertical offset at which to begin drawing
        Returns:
            None
        Raises:
            None
        """
        # Draw the table
        myTable = QgsComposerPicture(self.composition)
        myImage = self.renderImpactSummary()
        if myImage is not None:
            myTableFile = '/tmp/table.png'
            myImage.save(myTableFile, 'PNG')
            myTable.setPictureFile(myTableFile)
            myScaleFactor = 1
            myTableHeight = self.pointsToMM(myImage.height(),
                                             self.pageDpi) * myScaleFactor
            myTableWidth = self.pointsToMM(myImage.width(),
                                           self.pageDpi) * myScaleFactor
            myLeftOffset = self.pageMargin + 30
            myTable.setItemPosition(myLeftOffset,
                                    theTopOffset,
                                    myTableWidth,
                                    myTableHeight)
            myTable.setFrame(False)
            self.composition.addItem(myTable)

    def drawImpactTable(self, theTopOffset):
        """Render the impact table
        Args:
            theTopOffset - vertical offset at which to begin drawing
        Returns:
            None
        Raises:
            None
        """
        # Draw the table
        myTable = QgsComposerPicture(self.composition)
        myImage = self.renderImpactTable()
        if myImage is not None:
            myTableFile = '/tmp/table.png'
            myImage.save(myTableFile, 'PNG')
            myTable.setPictureFile(myTableFile)
            myScaleFactor = 1
            myTableHeight = self.pointsToMM(myImage.height(),
                                             self.pageDpi) * myScaleFactor
            myTableWidth = self.pointsToMM(myImage.width(),
                                           self.pageDpi) * myScaleFactor
            myLeftOffset = self.pageMargin + self.mapHeight - myTableWidth
            myTable.setItemPosition(myLeftOffset,
                                    theTopOffset,
                                    myTableWidth,
                                    myTableHeight)
            myTable.setFrame(False)
            self.composition.addItem(myTable)

    def drawDisclaimer(self):
        """Add a disclaimer to the composition
        Args:
            None
        Returns:
            None
        Raises:
            None
        """
        myFontSize = 10
        myFontWeight = QtGui.QFont.Normal
        myItalicsFlag = True
        myFont = QtGui.QFont('verdana',
                             myFontSize,
                             myFontWeight,
                             myItalicsFlag)
        myLabel = QgsComposerLabel(self.composition)
        myLabel.setFont(myFont)
        myLabel.setText(self.disclaimer)
        myLabel.adjustSizeToText()
        myLabelHeight = 7.0  # mm determined using qgis map composer
        myLabelWidth = self.pageWidth   # item - position and size...option
        myLeftOffset = self.pageMargin
        myTopOffset = self.pageHeight - self.pageMargin
        myLabel.setItemPosition(myLeftOffset,
                                myTopOffset,
                                myLabelWidth,
                                myLabelHeight,
                                )
        myLabel.setFrame(self.showFramesFlag)
        self.composition.addItem(myLabel)

    def makePdf(self, theFilename):
        """Method to createa  nice little pdf map.

        Args:
            theFilename - a string containing a filename path with .pdf
            extension
        Returns:
            None
        Raises:
            Any exceptions raised by the RIAB library will be propogated.
        """
        self.setupComposition()
        self.setupPrinter(theFilename)
        # Keep track of our vertical positioning as we work our way down
        # the page placing elements on it.
        myTopOffset = self.pageMargin
        self.drawLogo(myTopOffset)
        myLabelHeight = self.drawTitle(myTopOffset)
        # Update the map offset for the next row of content
        myTopOffset += myLabelHeight + self.verticalSpacing
        myComposerMap = self.drawMap(myTopOffset)
        self.drawScaleBar(myComposerMap, myTopOffset)
        # Update the top offset for the next horizontal row of items
        myTopOffset += self.mapHeight + self.verticalSpacing
        myImpactTitleHeight = self.drawImpactTitle(myTopOffset)
        # Update the top offset for the next horizontal row of items
        if myImpactTitleHeight:
            myTopOffset += myImpactTitleHeight + self.verticalSpacing + 2
        self.drawLegend(myTopOffset)
        self.drawImpactSummary(myTopOffset)
        self.drawImpactTable(myTopOffset)
        self.drawDisclaimer()
        self.renderPrintout()

    def getMapTitle(self):
        """Get the map title from the layer keywords if possible
        Args:
            None
        Returns:
            None on error, otherwise the title
        Raises:
            Any exceptions raised by the RIAB library will be propogated.
        """
        try:
            myTitle = getKeywordFromFile(str(self.layer.source()), 'map_title')
            return myTitle
        except Exception, e:
            return None

    def renderImpactSummary(self):
        """Render the impact summary in the keywords if present. The table is
        an html table with a summary for the impact layer.
        Args:
            None
        Returns:
            None
        Raises:
            Any exceptions raised by the RIAB library will be propogated.
        """
        try:
            myHtml = getKeywordFromFile(str(self.layer.source()),
                                        'impact_summary')
            return self.renderHtml(myHtml, 300)
        except Exception, e:
            return None

    def renderImpactTable(self):
        """Render the table in the keywords if present. The table is an
        html table with statistics for the impact layer.
        Args:
            None
        Returns:
            None
        Raises:
            Any exceptions raised by the RIAB library will be propogated.
        """
        try:
            myHtml = getKeywordFromFile(str(self.layer.source()),
                                        'impact_table')
            return self.renderHtml(myHtml, 500)
        except Exception, e:
            return None

    def renderHtml(self, theHtml, theWidth):
        """Render some HTML to a pixmap..

        Args:
            * theHtml - HTML to be rendered. It is assumed that the html
              is a snippet only, containing no body element - a standard
              header and footer will be appended.
            * theWidth- width of the table in pixels
        Returns:
            A QPixmap
        Raises:
            Any exceptions raised by the RIAB library will be propogated.
        """
        myPage = QtWebKit.QWebPage()
        myFrame = myPage.mainFrame()
        myFrame.setScrollBarPolicy(QtCore.Qt.Vertical,
                                   QtCore.Qt.ScrollBarAlwaysOff)
        myFrame.setScrollBarPolicy(QtCore.Qt.Horizontal,
                                   QtCore.Qt.ScrollBarAlwaysOff)

        myHeader = self.htmlHeader()
        myFooter = self.htmlFooter()
        myHtml = myHeader + theHtml + myFooter
        myFrame.setHtml(myHtml)
        #file('/tmp/report.html', 'wt').write(myHtml).close()
        #print '\n\n\nPage:\n', myFrame.toHtml()
        #mySize = QtCore.QSize(600, 200)
        mySize = myFrame.contentsSize()
        mySize.setWidth(theWidth)
        myPage.setViewportSize(mySize)
        # Disabled for now but please keep this as we may want to render using
        # a QImage due to device constraints (eg. headless server)
        myQImageFlag = False
        if myQImageFlag:
            myImage = QtGui.QImage(mySize, QtGui.QImage.Format_ARGB32)
            myImage.fill(QtGui.QColor(255, 255, 255))
            myPainter = QtGui.QPainter(myImage)
            myFrame.render(myPainter)
            myPainter.end()
            return myImage
        else:  # render with qpixmap rather
            myPixmap = QtGui.QPixmap(mySize)
            myPixmap.fill(QtGui.QColor(255, 255, 255))
            myPainter = QtGui.QPainter(myPixmap)
            myFrame.render(myPainter)
            myPainter.end()
            return myPixmap

    def pointsToMM(self, thePoints, theDpi):
        """Convert measurement in points to one in mm
        Args:
            thePoints - distance in pixels
            theDpi - dots per inch for conversion
        Returns:
            mm converted value
        Raises:
            Any exceptions raised by the RIAB library will be propogated.
        """
        myMM = (float(thePoints) / theDpi) * 25.4
        return myMM

    def htmlHeader(self):
        """Get a standard html header for wrapping content in."""
        if self.header is None:
            self.header = utilities.htmlHeader()
        return self.header

    def htmlFooter(self):
        """Get a standard html footer for wrapping content in."""
        if self.footer is None:
            self.footer = utilities.htmlFooter()
        return self.footer

    def showComposer(self):
        """Show the composition in a composer view so the user can tweak it
        if they want to
        Args:
            None
        Returns:
            None
        Raises:
            None
        """
        myView = QgsComposerView(self.iface.mainWindow())
        myView.show()
