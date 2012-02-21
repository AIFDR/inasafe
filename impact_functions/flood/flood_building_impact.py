from impact_functions.core import FunctionProvider
from impact_functions.core import get_hazard_layer, get_exposure_layer
from storage.vector import Vector
from storage.utilities import ugettext as _


class FloodBuildingImpactFunction(FunctionProvider):
    """Risk plugin for flood impact on building data

    :param requires category=='hazard' and \
                    subcategory.startswith('flood') and \
                    layertype in ['raster', 'vector']

    :param requires category=='exposure' and \
                    subcategory.startswith('building') and \
                    layertype=='vector'
    """

    target_field = 'AFFECTED'
    plugin_name = 'Temporary Closed'

    def run(self, layers):
        """Risk plugin for tsunami population
        """

        threshold = 1.0  # Flood threshold [m]

        # Extract data
        H = get_hazard_layer(layers)    # Depth
        E = get_exposure_layer(layers)  # Building locations

        # FIXME (Ole): interpolate does not carry original name through,
        # so get_name gives "Vector Layer" :-)

        # Interpolate hazard level to building locations
        I = H.interpolate(E)

        # Extract relevant numerical data
        attributes = I.get_data()
        N = len(I)

        # List attributes to carry forward to result layer
        attribute_names = E.get_attribute_names()

        # Calculate population impact
        count = 0
        building_impact = []
        for i in range(N):
            if H.is_raster:
                # Get the interpolated depth
                x = float(attributes[i].values()[0])
                x = x > threshold
            elif H.is_vector:
                # Use interpolated polygon attribute
                x = attributes[i]['Affected']

            # Tag and count
            if x is True:
                affected = 1
                count += 1
            else:
                affected = 0

            # Collect depth and calculated damage
            result_dict = {self.target_field: x}

            # Carry all original attributes forward
            for key in attributes:
                result_dict[key] = E.get_data(key, i)

            # Record result for this feature
            building_impact.append(result_dict)

        # Create report
        Hname = H.get_name()
        Ename = E.get_name()
        caption = _('<b>In case of "%s" the estimated impact to "%s" '
                   'the possibility of &#58;</b><br><br><p>' % (Hname,
                                                                Ename))
        caption += ('<table border="0" width="320px">'
                   '   <tr><th><b>%s</b></th><th><b>%s</b></th></th>'
                    '   <tr></tr>'
                    '   <tr><td>%s &#58;</td><td>%i</td></tr>'
                    '   <tr><td>%s &#58;</td><td>%i</td></tr>'
                    '   <tr><td>%s &#58;</td><td>%i</td></tr>'
                    '</table>' % (_('Building'), _('Number of'),
                                  _('All'), N,
                                  _('Closed'), count,
                                  _('Opened'), N - count))

        caption += '<br>'  # Blank separation row
        caption += '<b>' + _('Assumption') + '&#58;</b><br>'
        caption += _('Buildings that will need to closed when flooding'
                   'more than %.1f m' % threshold)

        # Create style
        style_classes = [dict(label=_('Opened'), min=0, max=0,
                              colour='#1EFC7C', opacity=1),
                         dict(label=_('Closed'), min=1, max=1,
                              colour='#F31A1C', opacity=1)]
        style_info = dict(target_field=self.target_field,
                          style_classes=style_classes)

        # Create vector layer and return
        V = Vector(data=building_impact,
                   projection=E.get_projection(),
                   geometry=E.get_geometry(),
                   name=_('Estimated buildings affected'),
                   keywords={'caption': caption},
                   style_info=style_info)
        return V
