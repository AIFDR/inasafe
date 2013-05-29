"""
InaSAFE Disaster risk assessment tool developed by AusAid - **Paragraph.**

Contact : ole.moller.nielsen@gmail.com

.. note:: This program is free software; you can redistribute it and/or modify
     it under the terms of the GNU General Public License as published by
     the Free Software Foundation; either version 2 of the License, or
     (at your option) any later version.
"""

__author__ = 'marco@opengis.ch'
__revision__ = '$Format:%H$'
__date__ = '28/05/2013'
__copyright__ = ('Copyright 2012, Australia Indonesia Facility for '
                 'Disaster Reduction')

from text import Text


class LinkText(Text):
    """A class to model emphasized text in the messaging system """

    def __init__(self, uri, text=None):
        """Creates a Emphasized Text Text object

        Args:
            String message, a string to add to the message

        Returns:
            None

        Raises:
            Errors are propagated
        """
        if text is None:
            text = uri

        self.uri = uri
        self.text = text

    def to_html(self):
        """Render as html

        Args:
            None

        Returns:
            Str the html representation

        Raises:
            Errors are propagated
        """
        return '<a href="%s">%s</a>' % (self.uri, self.text)

    def to_text(self):
        """Render as plain text

        Args:
            None

        Returns:
            Str the plain text representation

        Raises:
            Errors are propagated
        """
        if self.uri == self.text:
            return '::%s' % self.uri
        return '::%s [%s]' % (self.text, self.uri)
