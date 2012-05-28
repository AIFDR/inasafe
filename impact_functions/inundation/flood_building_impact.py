from impact_functions.core import FunctionProvider
from impact_functions.core import get_hazard_layer, get_exposure_layer
from storage.vector import Vector
from storage.utilities import ugettext as _


class FloodBuildingImpactFunction(FunctionProvider):
    """Risk plugin for flood impact on building data

    :param requires category=='hazard' and \
                    subcategory in ['flood', 'tsunami'] and \
                    layertype in ['raster', 'vector']

    :param requires category=='exposure' and \
                    subcategory=='building' and \
                    layertype=='vector' and \
                    purpose != 'dki'  # *
    """

  # FIXME (Ole): * Bring back when tabled and translated

    target_field = 'AFFECTED'
    plugin_name = _('Be temporarily closed')

    def run(self, layers):
        """Risk plugin for tsunami population
        """

        threshold = 1.0  # Flood threshold [m]

        # Extract data
        H = get_hazard_layer(layers)    # Depth
        E = get_exposure_layer(layers)  # Building locations

        # Interpolate hazard level to building locations
        I = H.interpolate(E, attribute_name='flood_level')

        # Extract relevant numerical data
        attributes = I.get_data()
        N = len(I)

        # Calculate population impact
        count = 0
        for i in range(N):
            if H.is_raster:
                # Get the interpolated depth
                x = float(attributes[i]['flood_level'])
                x = x > threshold
            elif H.is_vector:
                # Use interpolated polygon attribute
                x = attributes[i]['Affected']

            # Tag and count
            if x is True:
                count += 1

            # Add calculated impact to existing attributes
            attributes[i][self.target_field] = x

        # Create report
        Hname = H.get_name()
        Ename = E.get_name()
        impact_summary = _('<b>In case of "%s" the estimated impact to '
                           '"%s" is&#58;</b><br><br><p>' % (Hname,
                                                            Ename))
        impact_summary += ('<table border="0" width="320px">'
                   '   <tr><th><b>%s</b></th><th><b>%s</b></th></th>'
                    '   <tr></tr>'
                    '   <tr><td>%s &#58;</td><td>%i</td></tr>'
                    '   <tr><td>%s &#58;</td><td>%i</td></tr>'
                    '   <tr><td>%s &#58;</td><td>%i</td></tr>'
                    '</table>' % (_('Status'), _('Number of buildings'),
                                  _('Closed'), count,
                                  _('Open'), N - count,
                                  _('All'), N))

        impact_summary += '<br>'  # Blank separation row
        impact_summary += '<b>' + _('Assumptions') + '&#58;</b><br>'
        impact_summary += _('Buildings will need to close if flood'
                            ' levels exceed %.1f m' % threshold)

        # Create style
        style_classes = [dict(label=_('Open'), min=0, max=0,
                              colour='#1EFC7C', transparency=0, size=1),
                         dict(label=_('Closed'), min=1, max=1,
                              colour='#F31A1C', transparency=0, size=1)]
        style_info = dict(target_field=self.target_field,
                          style_classes=style_classes)

        # Create vector layer and return
        V = Vector(data=attributes,
                   projection=I.get_projection(),
                   geometry=I.get_geometry(),
                   name=_('Estimated buildings affected'),
                   keywords={'impact_summary': impact_summary},
                   style_info=style_info)
        return V
