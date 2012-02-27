"""
Disaster risk assessment tool developed by AusAid - **Help Dialog.**

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


from PyQt4 import QtGui, QtCore
from ui_riabhelp import Ui_RiabHelp
import os


class RiabHelp(QtGui.QDialog):
    """Help dialog class for the Risk In A Box plugin."""

    def __init__(self, theParent=None, theContext=None):
        """Constructor for the dialog.

        This dialog will show the user help documentation.

        Args:
           * theParent - Optional widget to use as parent
           * theContext - Optional - page name (without path)
             of a document in the user-docs subdirectory.
             e.g. 'keywords'
        Returns:
           not applicable
        Raises:
           no exceptions explicitly raised
        """
        QtGui.QDialog.__init__(self, theParent)
        # Set up the user interface from Designer.
        self.ui = Ui_RiabHelp()
        self.ui.setupUi(self)
        self.context = theContext
        self.showContexthelp()

    def showContexthelp(self):
        """Load the help text into the wvResults widget"""
        ROOT = os.path.dirname(__file__)
        myPath = os.path.abspath(os.path.join(ROOT, '..', 'docs', 'build',
                                            'html', 'user-docs',
                                            'README.html'))

        if self.context is not None:
            myContextPath = os.path.abspath(os.path.join(ROOT, '..',
                                            'docs', 'build',
                                            'html', 'user-docs',
                                            self.context + '.html'))
            if os.path.isfile(myContextPath):
                myPath = myContextPath
        self.ui.webView.setUrl(QtCore.QUrl('file:///' + myPath))
