"""
InaSAFE Disaster risk assessment tool developed by AusAid -
**Inasafe Lightmaps Widget.**

Contact : ole.moller.nielsen@gmail.com

.. note:: This program is free software; you can redistribute it and/or modify
     it under the terms of the GNU General Public License as published by
     the Free Software Foundation; either version 2 of the License, or
     (at your option) any later version.

"""

__author__ = 'bungcip@gmail.com'
__revision__ = '$Format:%H$'
__date__ = '5/02/2013'
__copyright__ = ('Copyright 2013, Australia Indonesia Facility for '
                 'Disaster Reduction')


from third_party.lightmaps import LightMaps, SlippyMap, tdim


ZOOM_LEVEL_DEGREE = [
    360,
    180,
    90,
    45,
    22.5,
    11.25,
    5.625,
    2.813,
    1.406,
    0.703,
    0.352,
    0.176,
    0.088,
    0.044,
    0.022,
    0.011,
    0.005,
    0.003,
    0.001
]


class InasafeSlippyMap(SlippyMap):
    """
    Class that implement map widget based on tile osm api.
    """

    def invalidate(self, theEmitSignal=True):
        """ Function that called every time the widget is updated
        Params:
            * theEmitSignal : bool - if true then the widget will
                                     emit signal "updated"
        """
        SlippyMap.invalidate(self, theEmitSignal)
        self.calculateExtent()

    def flipNumber(self, theNumber, theLimit):
        """
        This function will return a number which always in range of
        -limit and +limit. When the number is out of range, the number
        will wrap around.
        Params:
            * theNumber - the number
            * theLimit  - the limit of range in positive
        Return:
            a number in range of -limit and +limit
        """
        while theNumber > theLimit:
            theNumber = theNumber - (2 * theLimit)

        while theNumber < -theLimit:
            theNumber = theNumber + (2 * theLimit)

        return theNumber

    def calculateExtent(self):
        """
        Calculate top left & bottom right coordinate position
        of widget in mercator projection.

        The function will fill self.trLat (top left latitude),
        self.trLng (top left longitude),
        self.brLat (bottom right latitude)
        self.brLng (bottom right longitude)
        """
        myDegree = ZOOM_LEVEL_DEGREE[self.zoom]
        myTileCountX = float(self.width) / tdim
        myWidthInDegree = myTileCountX * myDegree
        myTileCountY = float(self.height) / tdim
        myHeightInDegree = myTileCountY * myDegree
        myOffsetX = myWidthInDegree / 2
        myOffsetY = myHeightInDegree / 2

        myMinY = self.latitude - myOffsetY
        myMinX = self.longitude - myOffsetX

        myMaxY = self.latitude + myOffsetY
        myMaxX = self.longitude + myOffsetX

        self.tlLat = self.flipNumber(myMinY, 90)
        self.brLat = self.flipNumber(myMaxY, 90)
        self.tlLng = self.flipNumber(myMinX, 180)
        self.brLng = self.flipNumber(myMaxX, 180)


class InasafeLightMaps(LightMaps):
    """
    Widget that contain slippy map
    """
    def __init__(self, parent):
        LightMaps.__init__(self, parent, InasafeSlippyMap)

    def getExtent(self):
        """
        Get extent of widget in mercator projection.
        Return:
         A tuple with format like this
        (top left latitude, top left longitude,
         bottom right latitude, bottom right longitude)
        """

        return (self.m_normalMap.tlLat, self.m_normalMap.tlLng,
                self.m_normalMap.brLat, self.m_normalMap.brLng)
