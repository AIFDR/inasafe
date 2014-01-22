
from PyQt4.QtCore import QVariant
from qgis.core import (
    QgsField,
    QgsVectorLayer,
    QgsFeature,
    QgsRectangle,
    QgsFeatureRequest,
    QgsGeometry,
    QgsCoordinateReferenceSystem,
    QgsCoordinateTransform
)

from safe.common.utilities import OrderedDict
from safe.impact_functions.core import FunctionProvider
from safe.impact_functions.core import get_hazard_layer, get_exposure_layer
from safe.impact_functions.core import get_question
from safe.common.tables import Table, TableRow
from safe.common.utilities import ugettext as tr
from safe.storage.vector import Vector
from safe.common.utilities import get_utm_epsg
from safe.common.exceptions import GetDataError
from safe.common.qgis_raster_tools import polygonize, clip_raster
from safe.common.qgis_vector_tools import split_by_polygon



class FloodRasterRoadsExperimentalFunction(FunctionProvider):
    """
    Simple experimental impact function for inundation

    :author Dmitry Kolesov
    :rating 1
    :param requires category=='hazard' and \
                    subcategory in ['flood', 'tsunami'] and \
                    layertype=='raster'
    :param requires category=='exposure' and \
                    subcategory in ['road'] and \
                    layertype=='vector'
    """

    title = tr('Be flooded in given thresholds')

    parameters = OrderedDict([
        # This field of impact layer marks inundated roads by '1' value
        ('target_field', 'flooded'),
        # This field of the exposure layer contains
        # information about road types
        ('road_type_field', 'TYPE'),
        ('min threshold [m]', 3.5),
        ('max threshold [m]', float('inf')),

         ('postprocessors', OrderedDict([('RoadType', {'on': True})]))
    ])

    def get_function_type(self):
        """Get type of the impact function.

        :returns:   'qgis2.0'
        """
        return 'qgis2.0'

    def set_extent(self, extent):
        """
        Set up the extent of area of interest ([xmin, ymin, xmax, ymax]).

        Mandatory method.
        """
        self.extent = extent

    def run(self, layers):
        """
        Experimental impact function

        Input
          layers: List of layers expected to contain
              H: Polygon layer of inundation areas
              E: Vector layer of roads
        """
        target_field = self.parameters['target_field']
        road_type_field = self.parameters['road_type_field']
        threshold_min = self.parameters['min threshold [m]']
        threshold_max = self.parameters['max threshold [m]']

        if threshold_min > threshold_max:
            message = tr('''The minimal threshold is
                greater then the maximal specified threshold.
                Please check the values.''')
            raise GetDataError(message)


        # Extract data
        H = get_hazard_layer(layers)    # Flood
        E = get_exposure_layer(layers)  # Roads

        question = get_question(H.get_name(),
                                E.get_name(),
                                self)

        H = H.get_layer()
        E = E.get_layer()

        e_provider = E.dataProvider()
        fields = e_provider.fields()
        # If target_field does not exist, add it:
        if fields.indexFromName(target_field) == -1:
            e_provider.addAttributes([QgsField(target_field,
                                               QVariant.Int)])
        target_field_index = e_provider.fieldNameIndex(target_field)


        # Get necessary width and height of raster
        height = (self.extent[3] - self.extent[1]) / H.rasterUnitsPerPixelY()
        height = int(height)
        width = (self.extent[2] - self.extent[0]) / H.rasterUnitsPerPixelX()
        width = int(width)

        small_raster = clip_raster(H, width, height, QgsRectangle(*self.extent))
        flooded_polygon = polygonize(small_raster, threshold_min, threshold_max)

        # Filter geometry and data using the extent
        extent = QgsRectangle(*self.extent)
        request = QgsFeatureRequest()
        request.setFilterRect(extent)

        if flooded_polygon is None:
            message = tr('''There are no objects
                in the hazard layer with
                "value">'%s'.
                Please check the value or use other
                extent.''' % (threshold_min, ))
            raise GetDataError(message)

        # Set roads as not inundated by default
        E.startEditing()
        e_data = E.getFeatures(request)
        for feat in e_data:
            feat.setAttribute(target_field_index, 0)
            E.updateFeature(feat)
        E.commitChanges()
        # Find inundated roads, mark them
        line_layer = split_by_polygon(E,
                                      flooded_polygon,
                                      request,
                                      mark_value=(target_field_index, 1))

        # Generate simple impact report
        epsg = get_utm_epsg(self.extent[0], self.extent[1])
        crs_dest = QgsCoordinateReferenceSystem(epsg)
        transform = QgsCoordinateTransform(E.crs(), crs_dest)
        road_len = flooded_len = 0  # Length of roads
        roads_by_type = dict()      # Length of flooded roads by types

        roads_data = line_layer.getFeatures()
        road_type_field_index = line_layer.fieldNameIndex(road_type_field)
        for road in roads_data:
            attrs = road.attributes()
            road_type = attrs[road_type_field_index]
            geom = road.geometry()
            geom.transform(transform)
            length = geom.length()
            road_len += length

            if not road_type in roads_by_type:
                roads_by_type[road_type] = {'flooded': 0, 'total': 0}
            roads_by_type[road_type]['total'] += length

            if attrs[target_field_index] == 1:
                flooded_len += length
                roads_by_type[road_type]['flooded'] += length
        table_body = [question,
                      TableRow([tr('Road Type'),
                                tr('Flooded in the threshold (m)'),
                                tr('Total (m)')],
                               header=True),
                      TableRow([tr('All'), int(flooded_len), int(road_len)])]
        table_body.append(TableRow(tr('Breakdown by road type'),
                                       header=True))
        for t, v in roads_by_type.iteritems():
            table_body.append(
                TableRow([t, int(v['flooded']), int(v['total'])])
            )

        impact_summary = Table(table_body).toNewlineFreeString()
        map_title = tr('Roads inundated')

        style_classes = [dict(label=tr('Not Inundated'), value=0,
                              colour='#1EFC7C', transparency=0, size=0.5),
                         dict(label=tr('Inundated'), value=1,
                              colour='#F31A1C', transparency=0, size=0.5)]
        style_info = dict(target_field=target_field,
                          style_classes=style_classes,
                          style_type='categorizedSymbol')

        # Convert QgsVectorLayer to inasafe layer and return it
        line_layer = Vector(data=line_layer,
                   name=tr('Flooded roads'),
                   keywords={'impact_summary': impact_summary,
                             'map_title': map_title,
                             'target_field': target_field},
                   style_info=style_info)
        return line_layer
