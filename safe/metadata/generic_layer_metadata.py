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
from safe.metadata.base_metadata import BaseMetadata


class GenericLayerMetadata(BaseMetadata):

    def __init__(self, layer_uri, xml_uri=None, json_uri=None):
        # Initialise members
        # public members
        self.report = None

        # initialize base class
        super(GenericLayerMetadata, self).__init__(
            layer_uri, xml_uri, json_uri)

    @property
    def dict(self):
        metadata = super(GenericLayerMetadata, self).dict
        metadata['report'] = self.report
        return metadata

    @property
    def json(self):
        return json.dumps(self.dict, indent=2, sort_keys=True)

    @property
    def xml(self):
        # TODO (MB): implement this
        xml = super(GenericLayerMetadata, self).xml
        raise NotImplementedError('Still need to write this')

    def read_from_json(self):
        metadata = super(GenericLayerMetadata, self).read_from_json()
        try:
            self.report = metadata['report']
        except KeyError:
            pass  # we want to get as much as we can without raising errors

    def read_from_xml(self):
        # TODO (MB): implement this
        super(GenericLayerMetadata, self).read_from_xml()

    def update_report(self):
        # TODO (MB) implement this by reading the kw and definitions.py
        self.report = self.report
