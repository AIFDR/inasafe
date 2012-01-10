"""
 Disaster risk assessment tool developed by AusAid - GUI Dialog.

 Contact : ole.moller.nielsen@gmail.com
"""

__author__ = 'tim@linfiniti.com'
__version__ = '0.0.1'
__date__ = '10/01/2011'
__copyright__ = 'Copyright 2012, Australia Indonesia Facility for '
__copyright__ += 'Disaster Reduction'

"""
***************************************************************************
*                                                                         *
*   This program is free software; you can redistribute it and/or modify  *
*   it under the terms of the GNU General Public License as published by  *
*   the Free Software Foundation; either version 2 of the License, or     *
*   (at your option) any later version.                                   *
*                                                                         *
***************************************************************************
"""

from PyQt4 import QtCore, QtGui
from ui_riab import Ui_Riab
DEBUG=True
if DEBUG:
    import sys 
    #todo: softcode this path!
    sys.path.append("/home/timlinux/.eclipse/org.eclipse.platform_3.7.0_155965261/plugins/org.python.pydev.debug_2.3.0.2011121518/pysrc/")
    from pydevd import *
  
class RiabDialog(QtGui.QDialog):
    """Dialog implementation class for the Risk In A Box plugin."""
    
    def __init__(self,iface):
        """Constructor for the dialog.
        
        This dialog will allow the user to select layers and scenario details and subsequently
        run their model.
        
        Args:
           iface - a Quantum GIS QGisAppInterface instance.
        Returns:
           not applicable
        Raises:
           no exceptions explicitly raised
        """
        settrace()
        QtGui.QDialog.__init__(self)
        # Save reference to the QGIS interface
        self.iface = iface
        # Set up the user interface from Designer.
        self.ui = Ui_Riab()
        self.ui.setupUi(self)
        self.getLayers()
       
    def getLayers(self):
        """Helper function to obtain a list of layers currently loaded in QGIS..
        
        On invocation, this method will populate the lstLayers on the dialog with a 
        list of available layers.
        
        Args:
           None.
        Returns:
           None
        Raises:
           no
        """
        for i in range(len(self.iface.mapCanvas().layers())):
            myLayer = self.iface.mapCanvas().layer(i)
            if myLayer.type() == myLayer.VectorLayer and myLayer.isUsingRendererV2():
                #if myLayer.geometryType() == QGis.Polygon:
                self.ui.lstLayers.addItem(myLayer.name()) #,myLayer.id())
        return

