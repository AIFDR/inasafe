

# coding=utf-8
"""
InaSAFE Disaster risk assessment tool developed by AusAid -
**Building Exposure Report Mixin Class**

Contact : ole.moller.nielsen@gmail.com

.. note:: This program is free software; you can redistribute it and/or modify
     it under the terms of the GNU General Public License as published by
     the Free Software Foundation; either version 2 of the License, or
     (at your option) any later version.
"""
__author__ = 'Samweli Twesa Mwakisambwe "Samweli" <smwltwesa6@gmail.com>'
__date__ = '13/10/15'

from collections import OrderedDict

from safe.utilities.i18n import tr
from safe.impact_reports.report_mixin_base import ReportMixin

import safe.messaging as m


class AreaExposureReportMixin(ReportMixin):
    """Population specific report.
    """

    def __init__(self):
        """Area specific report mixin.

        .. versionadded:: 3.2

        ..Notes::


        """
        self._question = ''
        self._areas = {}
        self._affected_areas = {}
        self._areas_population = {}
        self._total_population = 0
        self._unaffected_population = 0
        self._affected_population = {}
        self._other_population_counts = {}

    def generate_report(self):
        """Breakdown by building type.

        :returns: The report.
        :rtype: list
        """
        message = m.Message()
        message.add(m.Paragraph(self.question))
        message.add(self.impact_summary())

        return message

    def impact_summary(self):
        """The impact summary as per category

        :returns: The impact summary.
        :rtype: safe.messaging.Message
        """
        message = m.Message(style_class='container')
        table = m.Table(style_class='table table-condensed table-striped')
        table.caption = None

        row = m.Row()
        row.add(m.Cell(tr('Area id'), header=True))
        row.add(m.Cell(tr('Affected Area (ha)'), header=True))
        row.add(m.Cell(tr('Affected Area (%)'), header=True))
        row.add(m.Cell(tr('Total (ha)'), header=True))
        row.add(m.Cell(tr('Affected People'), header=True))
        row.add(m.Cell(tr('Affected People(%)'), header=True))
        row.add(m.Cell(tr('Total Number of People'), header=True))

        table.add(row)

        second_row = m.Row()
        second_row.add(m.Cell(tr('All')))
        total_affected_area = self.total_affected_areas
        total_area = self.total_areas
        percentage_affected_area = ((total_affected_area / total_area ) \
                                    if total_area != 0 else 0) * 100
        percentage_affected_area = round(percentage_affected_area, 1)

        total_affected_population = self.total_affected_population
        total_population = self.total_population
        percentage_affected_people = ((total_affected_population / total_population ) \
                                    if total_population != 0 else 0) * 100
        percentage_affected_people = round(percentage_affected_people, 1)
        total_affected_area *= 1e8
        total_affected_area = round(total_affected_area, 0)
        total_area *= 1e8
        total_area = round(total_area, 0)

        second_row.add(m.Cell(total_affected_area))
        second_row.add(m.Cell(percentage_affected_area))
        second_row.add(m.Cell(total_area))
        second_row.add(m.Cell(total_affected_population))
        second_row.add(m.Cell(percentage_affected_area))
        second_row.add(m.Cell(total_population))

        table.add(second_row)

        break_row = m.Row()
        break_row.add(m.Cell(tr('Breakdown by Area'), header=True))
        table.add(break_row)

        areas = self.areas
        affected_areas = self.affected_areas

        for t, v in areas.iteritems():
            affected = affected_areas[t] if t in affected_areas else 0.
            single_total_area = v
            affected_area_ratio = (affected / single_total_area) if v != 0 else 0

            percent_affected = affected_area_ratio * 100
            percent_affected = round(percent_affected, 1)
            number_people_affected = affected_area_ratio * self.areas_population[t]

            # rounding to float without decimal, we can't have number of people with decimal

            number_people_affected = round(number_people_affected, 0)

            percent_people_affected = ((number_people_affected / self.areas_population[t]) \
                                         if self.areas_population[t] != 0 else 0) * 100

            affected *= 1e8
            single_total_area *= 1e8

            row = m.Row()
            row.add(m.Cell(t))
            row.add(m.Cell("%.0f" % affected))
            row.add(m.Cell("%.1f%%" % percent_affected))
            row.add(m.Cell("%.0f" % single_total_area))
            row.add(m.Cell("%.0f" % number_people_affected))
            row.add(m.Cell("%.1f%%" % percent_people_affected))
            row.add(m.Cell(self.areas_population[t]))
            table.add(row)

        message.add(table)

        return message

    @property
    def affected_population(self):
        """Get the affected population counts.

        :returns: Affected population counts.
        :rtype: dict
        """
        if not hasattr(self, '_affected_population'):
            self._affected_population = OrderedDict()
        return self._affected_population

    @affected_population.setter
    def affected_population(self, affected_population):
        """Set the affected population counts.
        :param affected_population: The population counts.
        :type affected_population: dict
        """
        self._affected_population = affected_population

    @property
    def question(self):
        """Get the impact function question.

        :returns: The impact function question.
        :rtype: basestring
        """
        if not hasattr(self, '_question'):
            self._question = ''
        return self._question

    @question.setter
    def question(self, question):
        """Set the impact function question.

        :param question: The question.
        :type question: basestring
        """
        self._question = question

    @property
    def unaffected_population(self):
        """Get the unaffected population count.

        :returns: The unaffected population count.
        :returns: int
        """
        if not hasattr(self, '_unaffected_population'):
            self._unaffected_population = 0
        return self._unaffected_population

    @unaffected_population.setter
    def unaffected_population(self, unaffected_population):
        """Set the unaffected population count.

        :param unaffected_population: The unaffected population count.
        :return: int
        """
        self._unaffected_population = unaffected_population

    @property
    def affected_areas(self):
        """Get the affected areas.

        :returns: affected areas.
        :rtype: {}.
        """
        return self._affected_areas

    @affected_areas.setter
    def affected_areas(self, affected_areas):
        """Set the affected areas.

        :param affected_areas: affected areas.
        :type affected_areas:dict
        """
        self._affected_areas = affected_areas

    @property
    def total_affected_areas(self):
        """Get the total affected areas.

        :returns: Total affected areas.
        :rtype: int.
        """
        return sum(self.affected_areas.values())

    @property
    def areas_population(self):
        """Get the areas population.

        :returns: areas population.
        :rtype: dict.
        """
        return self._areas_population

    @areas_population.setter
    def areas_population(self, areas_population):
        """Set the areas population.

        :param areas_population: area population.
        :type areas_population:dict
        """
        self._areas_population = areas_population

    @property
    def total_areas_population(self):
        """Get the total affected areas.

        :returns: Total affected areas.
        :rtype: int.
        """
        return sum(self.areas_population.values())

    @property
    def total_areas(self):
        """Get the total area.

        :returns: Total area.
        :rtype: int.
        """
        return sum(self.areas.values())

    @property
    def areas(self):
        """Get the areas.

        :returns: areas.
        :rtype: dict.
        """
        return self._areas

    @areas.setter
    def areas(self, areas):
        """Set the areas.

        :param areas.
        :type areas: dict
        """
        self._areas = areas

    @property
    def total_affected_population(self):
        """Get the total affected population.

        :returns: Total affected population.
        :rtype: int.
        """
        return sum(self.affected_population.values())

    @property
    def total_population(self):
        """Get the total population.

        :returns: The total population.
        :rtype: int
        """
        if not hasattr(self, '_total_population'):
            self._total_population = 0
        return self._total_population

    @total_population.setter
    def total_population(self, total_population):
        """Set the total population.

        :param total_population: The total population count.
        :type total_population: int
        """
        self._total_population = total_population
