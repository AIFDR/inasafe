"""
Disaster risk assessment tool developed by AusAid -
  **QGIS plugin implementation.**

Contact : ole.moller.nielsen@gmail.com

.. note:: This program is free software; you can redistribute it and/or modify
     it under the terms of the GNU General Public License as published by
     the Free Software Foundation; either version 2 of the License, or
     (at your option) any later version.

"""

__author__ = 'tim@linfiniti.com'
__version__ = '0.0.1'
__date__ = '10/01/2011'
__copyright__ = 'Copyright 2012, Australia Indonesia Facility for '
__copyright__ += 'Disaster Reduction'

import os

# Import the PyQt and QGIS libraries
from PyQt4.QtCore import (QObject,
                          QLocale,
                          QTranslator,
                          SIGNAL,
                          QCoreApplication,
                          Qt,
                          QSettings,
                          QVariant)
from PyQt4.QtGui import QAction, QIcon, QApplication
from riabexceptions import TranslationLoadException
# Import RIAB modules
from riabdock import RiabDock
#see if we can import pydev - see development docs for details
try:
    from pydevd import *
    print 'Remote debugging is enabled.'
    DEBUG = True
except Exception, e:
    print 'Debugging was disabled'


class Riab:
    """The QGIS interface implementation for the Risk in a box plugin.

    This class acts as the 'glue' between QGIS and our custom logic.
    It creates a toolbar and menubar entry and launches the RIAB user
    interface if these are activated.
    """

    def __init__(self, iface):
        """Class constructor.

        On instantiation, the plugin instance will be assigned a copy
        of the QGIS iface object which will allow this plugin to access and
        manipulate the running QGIS instance that spawned it.

        Args:
           iface - a Quantum GIS QGisAppInterface instance. This instance
           is automatically passed to the plugin by QGIS when it loads the
           plugin.
        Returns:
           None.
        Raises:
           no exceptions explicitly raised.
        """

        # Save reference to the QGIS interface
        self.iface = iface
        self.translator = None
        self.setupI18n()
        print QCoreApplication.translate('Riab', 'Translations loaded')

    def setupI18n(self):
        """Setup internationalisation for the plugin.

        See if QGIS wants to override the system locale
        and then see if we can get a valid translation file
        for whatever locale is effectively being used.

        Args:
           None.
        Returns:
           None.
        Raises:
           no exceptions explicitly raised.
        """
        myOverrideFlag = QSettings().value('locale/overrideFlag',
                                            QVariant(False)).toBool()
        myLocaleName = None
        if not myOverrideFlag:
            myLocaleName = QLocale.system().name()
        else:
            myLocaleName = QSettings().value('locale/userLocale',
                                            QVariant('')).toString()
        myRoot = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
        myTranslationPath = os.path.join(myRoot, 'gui', 'i18n',
                        'riab_' + str(myLocaleName) + '.qm')
        if os.path.exists(myTranslationPath):
            self.translator = QTranslator()
            myResult = self.translator.load(myTranslationPath)
            if not myResult:
                myMessage = 'Failed to load translation for %s' % myLocaleName
                raise TranslationLoadException(myMessage)
            QCoreApplication.installTranslator(self.translator)
        print QCoreApplication.translate('Riab', 'Translations loaded')

    def initGui(self):
        """Gui initialisation procedure (for QGIS plugin api).

        This method is called by QGIS and should be used to set up
        any graphical user interface elements that should appear in QGIS by
        default (i.e. before the user performs any explicit action with the
        plugin).

        Args:
           None.
        Returns:
           None.
        Raises:
           no exceptions explicitly raised.
        """
        self.dockWidget = None

        # Create action for plugin dockable window (show/hide)
        self.actionDock = QAction(QIcon(':/plugins/riab/icon.png'),
                                QCoreApplication.translate('Riab',
                                'Risk in a Box'), self.iface.mainWindow())
        self.actionDock.setStatusTip(QCoreApplication.translate(
                                'Riab', 'Show/hide Risk in a Box dock widget'))
        self.actionDock.setWhatsThis(QCoreApplication.translate(
                                'Riab', 'Show/hide Risk in a Box dock widget'))
        self.actionDock.setCheckable(True)
        self.actionDock.setChecked(True)
        QObject.connect(self.actionDock, SIGNAL('triggered()'),
                        self.showHideDockWidget)

        self.iface.addToolBarIcon(self.actionDock)
        self.iface.addPluginToMenu(QCoreApplication.translate(
                                    'Riab', 'Risk in a Box'), self.actionDock)

        # create dockwidget and tabify it with the legend
        self.dockWidget = RiabDock(self.iface)
        self.iface.addDockWidget(Qt.LeftDockWidgetArea, self.dockWidget)
        myLegendTab = self.iface.mainWindow().findChild(QApplication,
                                                        'Legend')
        if myLegendTab:
            self.iface.mainWindow().tabifyDockWidget(myLegendTab,
                                                     self.dockWidget)
            self.dockWidget.raise_()

    def unload(self):
        """Gui breakdown procedure (for QGIS plugin api).

        This method is called by QGIS and should be used to *remove*
        any graphical user interface elements that should appear in QGIS.

        Args:
           None.
        Returns:
           None.
        Raises:
           no exceptions explicitly raised.
        """
        # Remove the plugin menu item and icon
        self.iface.removePluginMenu(QCoreApplication.translate(
                                    'Riab', '&Risk in a Box'), self.actionDock)
        self.iface.removeToolBarIcon(self.actionDock)
        self.iface.mainWindow().removeDockWidget(self.dockWidget)
        self.dockWidget.setVisible(False)
        self.dockWidget.destroy()

    # Run method that performs all the real work
    def showHideDockWidget(self):
        """Gui run procedure.

        This slot is called when the user clicks the toolbar icon or
        menu item associated with this plugin. It will hide or show
        the dock depending on its current state.

        .. see also:: :func:`Riab.initGui`.

        Args:
           None.
        Returns:
           None.
        Raises:
           no exceptions explicitly raised.
        """
        if self.dockWidget.isVisible():
            self.dockWidget.setVisible(False)
        else:
            self.dockWidget.setVisible(True)
            self.dockWidget.raise_()
