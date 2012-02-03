import numpy

from impact_functions.core import FunctionProvider
from impact_functions.core import get_hazard_layer, get_exposure_layer
from storage.raster import Raster
from storage.utilities import ugettext as _


class TsunamiPopulationImpactFunction(FunctionProvider):
    """Risk plugin for tsunami impact on population data

    :param requires category=='hazard' and \
                    subcategory.startswith('tsunami') and \
                    layertype=='raster' and \
                    unit=='m'

    :param requires category=='exposure' and \
                    subcategory.startswith('population') and \
                    layertype=='raster'

    """

    def run(self, layers):
        """Risk plugin for tsunami population
        """

        thresholds = [0.2, 0.3, 0.5, 0.8, 1.0]
        #threshold = 1  # Depth above which people are regarded affected [m]

        # Identify hazard and exposure layers
        inundation = get_hazard_layer(layers)    # Tsunami inundation [m]
        population = get_exposure_layer(layers)  # Population density

        # Extract data as numeric arrays
        D = inundation.get_data(nan=0.0)  # Depth
        P = population.get_data(nan=0.0, scaling=True)  # Population density

        # Calculate impact as population exposed to depths > 1m
        I_map = numpy.where(D > thresholds[-1], P, 0)

        # Generate text with result for this study
        number_of_people_affected = numpy.nansum(I_map.flat)

        # Do breakdown

        # Create report
        caption = ('<table border="0" width="320px">'
                   '   <tr><th><b>%s</b></th><th><b>%s</b></th></th>'
                   '   <tr></tr>' % ('Ambang batas', 'Jumlah orang terdampak'))

        counts = []
        for i, threshold in enumerate(thresholds):
            I = numpy.where(D > threshold, P, 0)
            counts.append(numpy.nansum(I.flat))

            caption += '   <tr><td>%s m</td><td>%i</td></tr>' % (threshold,
                                                                 counts[i])

        caption += '</table>'

        # Create raster object and return
        R = Raster(I_map,
                   projection=inundation.get_projection(),
                   geotransform=inundation.get_geotransform(),
                   name='People affected by more than 1m of inundation',
                   keywords={'caption': caption})
        return R
