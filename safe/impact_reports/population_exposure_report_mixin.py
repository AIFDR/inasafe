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
__author__ = 'Christian Christelis <christian@kartoza.com>'
__revision__ = '$Format:%H$'
__date__ = '05/05/2015'
__copyright__ = ('Copyright 2012, Australia Indonesia Facility for '
                 'Disaster Reduction')

from collections import OrderedDict

from safe.utilities.i18n import tr
from safe.common.utilities import format_int
from safe.impact_reports.report_mixin_base import ReportMixin

from safe.impact_functions.core import evacuated_population_needs


class PopulationExposureReportMixin(ReportMixin):
    """Building specific report.
    """

    def __init__(self):
        """Population specific report mixin.

        .. versionadded:: 3.3

        ..Notes:
        Expect affected population as following:

            _affected_population = OrderedDict([
                (impact level, amount),
            e.g.
                (People in high hazard area, 1000),
                (People in medium hazard area, 100),
                (People in low hazard area, 5),
            )]

        """
        self._question = ''
        self._unaffected_population = 0
        self._affected_population = {}
        self._other_population_counts = {}
        self._category_ordering = []

    def generate_report(self):
        """Breakdown by building type.

        :returns: The report.
        :rtype: list
        """
        report = [{'content': self.question}]
        report += [{'content': ''}]  # Blank line to separate report sections
        report += self.impact_summary()
        report += [{'content': ''}]  # Blank line to separate report sections
        report += self.minimum_needs_breakdown()
        report += [{'content': ''}]  # Blank line to separate report sections
        report += self.action_checklist()
        report += [{'content': ''}]  # Blank line to separate report sections
        report += self.notes()
        return report

    def action_checklist(self):
        """Breakdown by building type.

        :returns: The buildings breakdown report.
        :rtype: list
        """

        return [
            {
                'content': tr('Action Checklist:'),
                'header': True
            },
            {
                'content': tr('How will warnings be disseminated?')
            },
            {
                'content': tr('How will we reach evacuated people?')
            },
            {
                'content': tr(
                    'Are there enough shelters and relief items available '
                    'for %s people?' % self.total_affected_population)
            },
            {
                'content': tr(
                    'If yes, where are they located and how will we '
                    'distribute them?')
            },
            {
                'content': tr(
                    'If no, where can we obtain additional relief items from '
                    'and how will we transport them to here?')
            }
        ]

    def impact_summary(self):
        """The impact summary as per category

        :returns: The impact summary.
        :rtype: list
        """
        impact_summary_report = []
        for category in self.category_ordering:
            population_in_category = self.lookup_category(category)
            impact_summary_report.append(
                {
                    'content': [tr(category), population_in_category],
                    'header': True
                })
        return impact_summary_report

    def minimum_needs_breakdown(self):
        """Breakdown by building type.

        :returns: The buildings breakdown report.
        :rtype: list
        """
        minimum_needs_breakdown_report = []
        total_population_affected = self.total_affected_population
        total_needs = evacuated_population_needs(
            total_population_affected, self.minimum_needs)
        for frequency, needs in total_needs.items():
            minimum_needs_breakdown_report.append(
                {
                    'content': [
                        tr('Needs should be provided %s' % frequency),
                        tr('Total')],
                    'header': True
                })
            for resource in needs:
                minimum_needs_breakdown_report.append(
                    {
                        'content': [
                            tr(resource['table name']),
                            tr(format_int(resource['amount']))]
                    })
        return minimum_needs_breakdown_report

    @property
    def category_ordering(self):
        if not hasattr(self, '_category_ordering'):
            self._category_ordering = []
        return self._category_ordering

    @category_ordering.setter
    def category_ordering(self, category_ordering):
        self._category_ordering = category_ordering

    @property
    def other_population_counts(self):
        if not hasattr(self, '_other_population_counts'):
            self._other_population_counts = {}
        return self._other_population_counts

    @other_population_counts.setter
    def other_population_counts(self):
        if not hasattr(self, '_other_population_counts'):
            self._other_population_counts = {}
        return self._other_population_counts

    @property
    def affected_population(self):
        if not hasattr(self, '_affected_population'):
            self._affected_population = {}
        return self._affected_population

    @affected_population.setter
    def affected_population(self, affected_population):
        self._affected_population = affected_population

    @property
    def question(self):
        if not hasattr(self, '_question'):
            self._question = ''
        return self._question

    @question.setter
    def question(self, question):
        self._question = question

    @property
    def unaffected_population(self):
        if not hasattr(self, '_unaffected_population'):
            self._unaffected_population = 0
        return self._unaffected_population

    @unaffected_population.setter
    def unaffected_population(self, unaffected_population):
        self._unaffected_population = unaffected_population

    @property
    def total_affected_population(self):
        return sum(self.affected_population.values())

    def lookup_category(self, category):
        if category in self.affected_population.keys():
            return self.affected_population[category]
        if category in self.other_population_counts.keys():
            return self.other_population_counts[category]
        if category in [
                tr('Population Not Affected'),
                tr('Unaffected Population')]:
            return self.unaffected_population
        if category in [
                tr('Total Impacted'),
                tr('People impacted'),
                tr('Total Population Affected')]:
            return self.total_affected_population