# coding=utf-8
"""
InaSAFE Disaster risk assessment tool by AusAid -**InaSAFE Wizard**

This module provides: Keyword Wizard Step: Extra Keywords

Contact : ole.moller.nielsen@gmail.com

.. note:: This program is free software; you can redistribute it and/or modify
     it under the terms of the GNU General Public License as published by
     the Free Software Foundation; either version 2 of the License, or
     (at your option) any later version.

"""
__author__ = 'qgis@borysjurgiel.pl'
__revision__ = '$Format:%H$'
__date__ = '16/03/2016'
__copyright__ = ('Copyright 2012, Australia Indonesia Facility for '
                 'Disaster Reduction')

# noinspection PyPackageRequirements
from PyQt4 import QtCore
from PyQt4.QtGui import (
    QGroupBox,
    QLineEdit,
    QLabel,
    QDialog,
    QCheckBox,
    QWidget,
    QScrollArea,
    QVBoxLayout)

from safe_extras.parameters.select_parameter import SelectParameter
from safe_extras.parameters.qt_widgets.parameter_container import (
    ParameterContainer)

from safe.definitionsv4.layer_modes import layer_mode_classified
from safe.definitionsv4.exposure import exposure_place
from safe.definitionsv4.utilities import get_fields
from safe.definitionsv4.layer_geometry import layer_geometry_raster
from safe.gui.tools.wizard.wizard_step import WizardStep
from safe.gui.tools.wizard.wizard_step import get_wizard_step_ui_class


FORM_CLASS = get_wizard_step_ui_class(__file__)


class StepKwExtraKeywords(WizardStep, FORM_CLASS):
    """Keyword Wizard Step: Extra Keywords"""

    def __init__(self, parent=None):
        """Constructor for the tab.

        :param parent: parent - widget to use as parent (Wizad Dialog).
        :type parent: QWidget

        """
        WizardStep.__init__(self, parent)

        self.parameters = []

    def is_ready_to_next_step(self):
        """Check if the step is complete. If so, there is
            no reason to block the Next button.

        :returns: True if new step may be enabled.
        :rtype: bool
        """
        return True

    def get_previous_step(self):
        """Find the proper step when user clicks the Previous button.

        :returns: The step to be switched to
        :rtype: WizardStep instance or None
        """
        selected_subcategory = self.parent.step_kw_subcategory.\
            selected_subcategory()
        if selected_subcategory == exposure_place:
            new_step = self.parent.step_kw_name_field
        elif self.parent.step_kw_layermode.\
                selected_layermode() == layer_mode_classified:
            if self.parent.step_kw_classification.selected_classification() \
                    or self.parent.step_kw_classify.\
                    postprocessor_classification_for_layer():
                new_step = self.parent.step_kw_classify
            elif self.parent.step_kw_field.selected_field():
                new_step = self.parent.step_kw_field
            else:
                new_step = self.parent.step_kw_layermode
        else:
            if self.parent.step_kw_resample.\
                    selected_allowresampling() is not None:
                new_step = self.parent.step_kw_resample
            else:
                new_step = self.parent.step_kw_unit
        return new_step

    def get_next_step(self):
        """Find the proper step when user clicks the Next button.

        :returns: The step to be switched to
        :rtype: WizardStep instance or None
        """
        new_step = self.parent.step_kw_source
        return new_step

    def additional_keywords_for_the_layer(self):
        """Return a list of inasafe fields the current layer.

        :returns: A list where each value represents inasafe field.
        :rtype: list
        """
        if (self.parent.get_layer_geometry_key() ==
                layer_geometry_raster['key']):
            return []
        return get_fields(
            self.parent.step_kw_purpose.selected_purpose()['key'])

    def extra_keyword_changed(self, widget):
        """Populate slave widget if exists and enable the Next button
           if all extra keywords are set.

        :param widget: Metadata of the widget where the event happened.
        :type widget: dict
        """

        self.parent.pbnNext.setEnabled(self.are_all_extra_keywords_selected())

    def selected_extra_keywords(self):
        """Obtain the extra keywords selected by user.

        :returns: Metadata of the extra keywords.
        :rtype: dict, None
        """
        extra_keywords = {}

        return extra_keywords

    def are_all_extra_keywords_selected(self):
        """Ensure all all additional keyword are set by user

        :returns: True if all additional keyword widgets are set
        :rtype: boolean
        """
        return True

    def populate_value_widget_from_field(self, widget, field_name):
        """Populate the slave widget with unique values of the field
           selected in the master widget.

        :param widget: The widget to be populated
        :type widget: QComboBox

        :param field_name: Name of the field to take the values from
        :type field_name: str
        """
        fields = self.parent.layer.dataProvider().fields()
        field_index = fields.indexFromName(field_name)
        widget.clear()
        for v in self.parent.layer.uniqueValues(field_index):
            widget.addItem(unicode(v), unicode(v))
        widget.setCurrentIndex(-1)

    def set_widgets(self):
        """Set widgets on the Extra Keywords tab."""
        # scroll_layout = QVBoxLayout()
        # scroll_widget = QWidget()
        # scroll_widget.setLayout(scroll_layout)
        # scroll = QScrollArea()
        # scroll.setWidgetResizable(True)
        # scroll.setWidget(scroll_widget)
        # main_layout = QVBoxLayout()
        # main_layout.addWidget(scroll)
        # main_widget = QWidget()
        # main_widget.setLayout(main_layout)

        # select_parameter = SelectParameter()
        # select_parameter.name = 'Select Affected Field'
        # select_parameter.is_required = True
        # select_parameter.help_text = 'Column used for affected field'
        # select_parameter.description = (
        #     'Column used for affected field in the vector')
        # select_parameter.element_type = str
        # select_parameter.options_list = [
        #     'FLOODPRONE', 'affected', 'floodprone', 'yes/no',
        #     '\xddounicode test']
        # select_parameter.value = 'affected'

        for i in self.additional_keywords_for_the_layer():
            select_parameter = SelectParameter()
            select_parameter.name = i['name']
            select_parameter.is_required = False
            select_parameter.help_text = i['description']
            select_parameter.description = i['description']
            select_parameter.element_type = str
            select_parameter.options_list = [
                'FLOODPRONE', 'affected', 'floodprone', 'yes/no',
                '\xddounicode test']
            select_parameter.value = 'affected'
            self.parameters.append(select_parameter)

        parameter_container = ParameterContainer(self.parameters)
        parameter_container.setup_ui()

        self.kwExtraKeywordsGridLayout.addWidget(parameter_container)

        # kwExtraKeywordsGridLayout

        # # Set and show used widgets
        # extra_keywords = self.additional_keywords_for_the_layer()
        # for i in range(len(extra_keywords)):
        #     extra_keyword = extra_keywords[i]
        #     extra_keywords_widget = self.extra_keywords_widgets[i]
        #     extra_keywords_widget['key'] = extra_keyword['key']
        #     extra_keywords_widget['lbl'].setText(extra_keyword['description'])
        #     if extra_keyword['type'] == 'value':
        #         field_widget = self.extra_keywords_widgets[i - 1]['cbo']
        #         field_name = field_widget.itemData(
        #             field_widget.currentIndex(), QtCore.Qt.UserRole)
        #         self.populate_value_widget_from_field(
        #             extra_keywords_widget['cbo'], field_name)
        #     else:
        #         for field in self.parent.layer.dataProvider().fields():
        #             field_name = field.name()
        #             field_type = field.typeName()
        #             extra_keywords_widget['cbo'].addItem('%s (%s)' % (
        #                 field_name, field_type), field_name)
        #     # If there is a master keyword, attach this widget as a slave
        #     # to the master widget. It's used for values of a given field.
        #     if ('master_keyword' in extra_keyword and
        #             extra_keyword['master_keyword']):
        #         master_key = extra_keyword['master_keyword']['key']
        #         for master_candidate in self.extra_keywords_widgets:
        #             if master_candidate['key'] == master_key:
        #                 master_candidate['slave_key'] = extra_keyword['key']
        #     # Show the widget
        #     extra_keywords_widget['cbo'].setCurrentIndex(-1)
        #     extra_keywords_widget['lbl'].show()
        #     extra_keywords_widget['cbo'].show()
        #
        # # Set values based on existing keywords (if already assigned)
        # for ekw in self.extra_keywords_widgets:
        #     if not ekw['key']:
        #         continue
        #     value = self.parent.get_existing_keyword(ekw['key'])
        #     indx = ekw['cbo'].findData(value, QtCore.Qt.UserRole)
        #     if indx != -1:
        #         ekw['cbo'].setCurrentIndex(indx)
