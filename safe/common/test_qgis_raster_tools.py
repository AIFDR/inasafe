
import os
import unittest

from safe.common.testing import UNITDATA, get_qgis_app
from safe.storage.raster import qgis_imported

if qgis_imported:   # Import QgsRasterLayer if qgis is available
    QGIS_APP, CANVAS, IFACE, PARENT = get_qgis_app()
    from qgis.core import (
        QgsRasterLayer,
        QgsRaster,
        QgsPoint,
        QgsApplication
        )


RASTER_BASE = os.path.abspath(
    os.path.join(UNITDATA, 'hazard', 'jakarta_flood_design'))

from qgis_raster_tools import (
    pixes_to_points,
    polygonize
    )


class Test_qgis_raster_tools(unittest.TestCase):

    def setUp(self):
        self.raster = QgsRasterLayer(RASTER_BASE + '.tif', 'test')
        self.provider = self.raster.dataProvider()
        self.extent = self.raster.extent()
        self.x_res = self.raster.rasterUnitsPerPixelX()
        self.y_res = self.raster.rasterUnitsPerPixelY()

    def test_pixes_to_points(self):
        points = pixes_to_points(self.raster,
                                 threshold_min=1.0,
                                 threshold_max=1.5)

        # There are four such pixels only
        self.assertEquals(points.featureCount(), 4)
        for point in points.dataProvider().getFeatures():
            point = point.geometry().asPoint()

            # Move point in center of the pixels and get the value
            value = self.provider.identify(QgsPoint(
                                                point.x() + 0.5*self.x_res,
                                                point.y() - 0.5*self.y_res),
                                           QgsRaster.IdentifyFormatValue,
                                           self.extent)
            value, _ = value.results()[1].toDouble()
            self.assertGreater(value, 1.0)
            self.assertLess(value, 1.5)

        # Infinite threshold test
        points = pixes_to_points(self.raster,
                                 threshold_min=1.1)
        self.assertEquals(points.featureCount(), 8)
        for point in points.dataProvider().getFeatures():
            point = point.geometry().asPoint()

            # Move point in center of the pixels and get the value
            value = self.provider.identify(QgsPoint(
                                                point.x() + 0.5*self.x_res,
                                                point.y() - 0.5*self.y_res),
                                           QgsRaster.IdentifyFormatValue,
                                           self.extent)
            value, _ = value.results()[1].toDouble()
            self.assertGreater(value, 1.1)
    test_pixes_to_points.slow = True


if __name__ == '__main__':
    suite = unittest.makeSuite(Test_qgis_raster_tools, 'test')
    runner = unittest.TextTestRunner()
    runner.run(suite)
