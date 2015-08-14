# -*- coding: utf-8 -*-
"""
InaSAFE Disaster risk assessment tool developed by AusAid -
**metadata module.**

Contact : ole.moller.nielsen@gmail.com

.. note:: This program is free software; you can redistribute it and/or modify
     it under the terms of the GNU General Public License as published by
     the Free Software Foundation; either version 2 of the License, or
     (at your option) any later version.
"""

__author__ = 'marco@opengis.ch'
__revision__ = '$Format:%H$'
__date__ = '27/05/2015'
__copyright__ = ('Copyright 2012, Australia Indonesia Facility for '
                 'Disaster Reduction')

import json
from xml.etree import ElementTree
from safe.metadata import BaseMetadata
from safe.metadata.utils import reading_ancillary_files


class GenericLayerMetadata(BaseMetadata):
    def __init__(self, layer_uri, xml_uri=None, json_uri=None):
        # initialize base class
        super(GenericLayerMetadata, self).__init__(
            layer_uri, xml_uri, json_uri)

    @property
    def dict(self):
        return super(GenericLayerMetadata, self).dict

    @property
    def json(self):
        return json.dumps(self.dict, indent=2, sort_keys=True)

    @property
    def xml(self):
        root = super(GenericLayerMetadata, self).xml
        return ElementTree.tostring(root)

    def read_json(self):
        with reading_ancillary_files(self):
            metadata = super(GenericLayerMetadata, self).read_json()

        return metadata

    def read_xml(self):
        with reading_ancillary_files(self):
            root = super(GenericLayerMetadata, self).read_xml()

        return root

    def update_report(self):
        # TODO (MB): implement this by reading the kw and definitions.py
        self.report = self.report
