# coding=utf-8
"""
InaSAFE Disaster risk assessment tool developed by AusAid -
**Impact Function Manager**

Contact : ole.moller.nielsen@gmail.com

.. note:: This program is free software; you can redistribute it and/or modify
     it under the terms of the GNU General Public License as published by
     the Free Software Foundation; either version 2 of the License, or
     (at your option) any later version.
"""

from safe.utilities.i18n import tr
from safe.common.utilities import format_int
from safe.impact_reports.report_mixin_base import ReportMixin


class BuildingExposureReportMixin(ReportMixin):

    def generate_report(self, question, affected_buildings, buildings):
        """Breakdown by building type.

        :param question: The impact question.
        :type question: basestring

        :param affected_buildings: The affected buildings
        :type affected_buildings: OrderedDict

        :param buildings: The buildings and totals.
        :type buildings: dict

        :returns: The report.
        :rtype: list
        """
        report = [{'content': question}]
        report += [{'content': ''}]  # Blank line to separate report sections
        report += self.impact_summary(affected_buildings)
        report += [{'content': ''}]  # Blank line to separate report sections
        report += self.buildings_breakdown(affected_buildings, buildings)
        report += [{'content': ''}]  # Blank line to separate report sections
        report += self.action_checklist(affected_buildings)
        report += [{'content': ''}]  # Blank line to separate report sections
        report += self.notes()
        return report

    def action_checklist(self, affected_buildings):
        """Breakdown by building type.

        :param affected_buildings: The affected buildings
        :type affected_buildings: OrderedDict

        :returns: The buildings breakdown report.
        :rtype: list

        ..Notes:
        Expect affected buildings to be given as following:
            affected_buildings = OrderedDict([
                (category, {building_type: amount}),
            e.g.
                (inundated, {residential: 1000, school: 0 ...}),
                (wet, {residential: 12, school: 2 ...}),
                (dry, {residential: 50, school: 50})
            ])
        """
        schools_closed = self.schools_closed(affected_buildings)
        hospitals_closed = self.hospitals_closed(affected_buildings)
        return [
            {
                'content': tr('Action Checklist:'),
                'header': True
            },
            {
                'content': tr('Are the critical facilities still open?')
            },
            {
                'content': tr(
                    'Which structures have warning capacity '
                    '(eg. sirens, speakers, etc.)?')},
            {
                'content': tr('Which buildings will be evacuation centres?')
            },
            {
                'content': tr('Where will we locate the operations centre?')
            },
            {
                'content': tr(
                    'Where will we locate warehouse and/or distribution '
                    'centres?')
            },
            {
                'content': tr(
                    'Where will the students from the %s closed schools go to '
                    'study?'),
                'arguments': (format_int(schools_closed),),
                'condition': schools_closed > 0
            },
            {
                'content': tr(
                    'Where will the patients from the %s closed hospitals go '
                    'for treatment and how will we transport them?'),
                'arguments': (format_int(hospitals_closed),),
                'condition': hospitals_closed > 0
            }
        ]

    def impact_summary(self, affected_buildings):
        """The impact summary as per category

        :returns:
        """
        affect_types = self._impact_breakdown(affected_buildings)
        impact_summary_report = [
            {
                'content': [tr('Hazard Category')] + affect_types,
                'header': True
            }]
        for (category, building_breakdown) in affected_buildings.items():
            total_affected = [0] * len(affect_types)
            for affected_breakdown in building_breakdown.values():
                for (affect_type, number_affected) in affected_breakdown.items():
                    count = affect_types.index(affect_type)
                    total_affected[count] += number_affected
            total_affected_formatted = [
                format_int(affected) for affected in total_affected]
            impact_summary_report.append(
                {
                    'content': [tr(category)] + total_affected_formatted
                })
        return impact_summary_report

    def buildings_breakdown(self, affected_buildings, buildings):
        """Breakdown by building type.

        :param affected_buildings: The affected buildings
        :type affected_buildings: OrderedDict

        :param buildings: The buildings totals
        :type buildings: dict

        :returns: The buildings breakdown report.
        :rtype: list

        ..Notes:
        Expect affected buildings to be given as following:
            affected_buildings = OrderedDict([
                (category, {building_type: amount}),
            e.g.
                (inundated, {
                    residential: OrderedDict([
                        (Buildings Affected, 1000),
                        (value, ...
                    ]),
                    school: OrderedDict([
                        (Buildings Affected, 0),
                        (value, ...
                    },
                    ...
                }),
                (wet, {
                    residential: OrderedDict([
                        (Buildings Affected, 12),
                        (value, ...
                    },
                    school: OrderedDict([
                        (Buildings Affected, 2),
                        (value, ...
                    }...
                }),
                (dry, {
                    residential: OrderedDict([
                        (Buildings Affected, 1),
                        (value, ...
                    },
                    school: {
                        (Buildings Affected, 5),
                        (value, ...
                    }...
                }),
            ])
            buildings = {residential: 1062, school: 52 ...}
        """
        buildings_breakdown_report = []
        category_names = affected_buildings.keys()
        table_headers = [tr('Building type')]
        table_headers += [tr(x) for x in category_names]
        table_headers += [tr('Total')]
        buildings_breakdown_report.append(
            {
                'content': table_headers,
                'header': True
            })
        # Let's sort alphabetically first
        building_types = [building_type for building_type in buildings]
        building_types.sort()
        for building_type in building_types:
            building_type = building_type.replace('_', ' ')
            affected_by_usage = []
            for category in category_names:
                if building_type in affected_buildings[category]:
                    affected_by_usage.append(
                        format_int(
                            affected_buildings[category][
                                building_type].values()[0]))
                else:
                    affected_by_usage.append(format_int(0))
            building_detail = (
                # building type
                [building_type.capitalize()] +
                # categories
                affected_by_usage +
                # total
                [format_int(buildings[building_type])])
            buildings_breakdown_report.append(
                {
                    'content': building_detail
                })

        return buildings_breakdown_report

    #This could be a property if we make affected_buildings a class property
    def schools_closed(self, affected_buildings):
        """Get the number of schools

        :param affected_buildings: The affected buildings
        :type affected_buildings: OrderedDict

        :returns: The buildings breakdown report.
        :rtype: list

        ..Notes:
        Expect affected buildings to be given as following:
            affected_buildings = OrderedDict([
                (category, {building_type: amount}),
            e.g.
                (inundated, {residential: 1000, school: 0 ...}),
                (wet, {residential: 12, school: 2 ...}),
                (dry, {residential: 50, school: 50})
            ])
        """
        return self._count_usage('school', affected_buildings)

    #This could also be a property if we make affected_buildings a class property
    def hospitals_closed(self, affected_buildings):
        """Get the number of schools

        :param affected_buildings: The affected buildings
        :type affected_buildings: OrderedDict

        :returns: The buildings breakdown report.
        :rtype: list

        ..Notes:
        Expect affected buildings to be given as following:
            affected_buildings = OrderedDict([
                (category, {building_type: amount}),
            e.g.
                (inundated, {residential: 1000, school: 0 ...}),
                (wet, {residential: 12, school: 2 ...}),
                (dry, {residential: 50, school: 50})
            ])
        """
        return self._count_usage('hospital', affected_buildings)

    @staticmethod  # While we have a static don't have affected_buildings as a
    def _count_usage(usage, affected_buildings):
        count = 0
        for category, category_breakdown in affected_buildings.items():
            for current_usage in category_breakdown:
                if current_usage.lower() == usage.lower():
                    count += category_breakdown[current_usage].values()[0]
        return count

    def _impact_breakdown(self, affected_buildings):
        return affected_buildings.values()[0].values()[0].keys()