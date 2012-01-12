'''
Disaster risk assessment tool developed by AusAid - **Exception Classes.**

Custom exception classes for the Riab application.

Contact : ole.moller.nielsen@gmail.com

.. note:: This program is free software; you can redistribute it and/or modify
     it under the terms of the GNU General Public License as published by
     the Free Software Foundation; either version 2 of the License, or
     (at your option) any later version.

'''

__author__ = 'tim@linfiniti.com'
__version__ = '0.0.1'
__date__ = '12/01/2011'
__copyright__ = ('Copyright 2012, Australia Indonesia Facility for '
                 'Disaster Reduction')

class QgisPathException(Exception):
  '''Custom exception for when qgispath.txt could not be read.'''
  pass
