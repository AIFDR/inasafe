# coding=utf-8
"""This is the concrete Minimum Needs class that contains the logic to load
the minimum needs to and from the QSettings"""

__author__ = 'Christian Christelis <christian@kartoza.com>'
__date__ = '05/10/2014'
__copyright__ = ('Copyright 2014, Australia Indonesia Facility for '
                 'Disaster Reduction')

# noinspection PyUnresolvedReferences
# pylint: disable=W0611
from qgis.core import QGis  # force sip2 api

from third_party.parameters.resource_parameter import ResourceParameter
from PyQt4.QtCore import QSettings, QFile, QDir
from qgis.core import QgsApplication
from safe.common.minimum_needs import MinimumNeeds
import json
import os


class NeedsProfile(MinimumNeeds):
    """The concrete MinimumNeeds class to be used in a QGIS environment.

    In the case where we assume QGIS we use the QSettings object to store the
    minimum needs.

    .. versionadded:: 2.2.
    """

    def __init__(self):
        self.settings = QSettings()
        self.minimum_needs = None
        self._root_directory = None
        self.locale = os.environ['LANG']
        self.load()

    def load(self):
        """Load the minimum needs from the QSettings object.
        """
        minimum_needs = self.settings.value('MinimumNeeds', )
        if hasattr(minimum_needs, 'toPyObject'):
            minimum_needs = minimum_needs.toPyObject()
        if minimum_needs is None:
            profiles = self.get_profiles()
            self.read_from_file(
                QFile('%s/minimum_needs/%s.json' % (
                    self.root_directory, profiles)))
        if minimum_needs is None:
            minimum_needs = self._defaults()
        self.minimum_needs = minimum_needs

    def load_profile(self, profile):
        """Load a specific profile into the current minimum needs.

        :param profile: The profile's name
        :type profile: basestring, str
        """
        self.read_from_file(
            QFile('%s/minimum_needs/%s.json' % (
                self.root_directory, profile)))

    def save_profile(self, profile):
        """Save the current minimum needs into a new profile.

        :param profile: The profile's name
        :type profile: basestring, str
        """
        profile = profile.replace('.json', '')
        self.write_to_file(
            QFile('%s/minimum_needs/%s.json' % (
                self.root_directory, profile)))

    def save(self):
        """Save the minimum needs to the QSettings object.
        """
        # This needs to be imported here to avoid an inappropriate loading
        # sequence
        if not self.minimum_needs['resources']:
            return
        from safe.impact_functions.core import get_plugins
        self.settings.setValue('MinimumNeeds', self.minimum_needs)
        # Monkey patch all the impact functions
        for (_, plugin) in get_plugins().items():
            if not hasattr(plugin, 'parameters'):
                continue
            if 'minimum needs' in plugin.parameters:
                plugin.parameters['minimum needs'] = (
                    self.get_needs_parameters())
                plugin.parameters['provenance'] = self.provenance

    def get_profiles(self):
        """Get all the minimum needs profiles.

        :returns: The minimum needs by name.
        :rtype: list
        """
        def sort_by_locale(unsorted_profiles, locale):
            """Sort the profiles by language settings

            :param unsorted_profiles: The user profiles profiles
            :type unsorted_profiles: list

            :param locale: The language settings string
            :type locale: str

            :returns: Ordered profiles
            :rtype: list
            """
            locale = '_%s' % locale[:2]
            profiles_our_locale = []
            profiles_remaining = []
            for profile_name in unsorted_profiles:
                if locale in profile_name:
                    profiles_our_locale.append(profile_name)
                else:
                    profiles_remaining.append(profile_name)

            return profiles_our_locale + profiles_remaining

        locale_minimum_needs_dir = QDir(
            '%s/minimum_needs/' % self.root_directory)
        path_name = "%s/../../../files/minimum_needs" % (
            os.path.dirname(__file__))
        plugins_minimum_needs_dir = QDir(path_name)
        if not locale_minimum_needs_dir.exists():
            if not plugins_minimum_needs_dir.exists():
                # This is specifically to get Travis working.
                return [self._defaults()['profile']]
            QDir(self.root_directory).mkdir('minimum_needs')
            for file_name in plugins_minimum_needs_dir.entryList():
                source_file = QFile(
                    '%s/python/plugins/inasafe/files/minimum_needs/%s' %
                    (self.root_directory, file_name))
                source_file.copy(
                    '%s/minimum_needs/%s' %
                    (self.root_directory, file_name))
        profiles = [
            profile[:-5] for profile in
            locale_minimum_needs_dir.entryList() if
            profile[-5:] == '.json']
        profiles = sort_by_locale(profiles, self.locale)
        return profiles

    def read_from_file(self, qfile):
        """Read from an existing json file.

        :param qfile: The object to be read from.
        :type qfile: QFile

        :returns: Success status. -1 for unsuccessful 0 for success
        :rtype: int
        """
        if not qfile.exists():
            return -1
        qfile.open(QFile.ReadOnly)
        needs_json = qfile.readAll()
        try:
            minimum_needs = json.loads('%s' % needs_json)
        except (TypeError, ValueError):
            minimum_needs = None

        if not minimum_needs:
            return -1

        return self.update_minimum_needs(minimum_needs)

    def write_to_file(self, qfile):
        """Write minimum needs as json to a file.

        :param qfile: The file to be written to.
        :type qfile: QFile
        """
        qfile.open(QFile.WriteOnly)
        needs_json = json.dumps(self.minimum_needs)
        qfile.write(needs_json)

    def get_needs_parameters(self):
        """Get the minimum needs resources in parameter format

        :returns: The minimum needs resources wrapped in parameters.
        :rtype: list
        """
        parameters = []
        for resource in self.minimum_needs['resources']:
            parameter = ResourceParameter()
            parameter.name = resource['Resource name']
            parameter.help_text = resource['Resource description']
            # Adding in the frequency property. This is not in the
            # FloatParameter by default, so maybe we should subclass.
            parameter.frequency = resource['Frequency']
            parameter.description = self.format_sentence(
                resource['Readable sentence'],
                resource)
            parameter.minimum_allowed_value = float(
                resource['Minimum allowed'])
            parameter.maximum_allowed_value = float(
                resource['Maximum allowed'])
            parameter.unit.name = resource['Unit']
            parameter.unit.plural = resource['Units']
            parameter.unit.abbreviation = resource['Unit abbreviation']
            parameter.value = float(resource['Default'])
            parameters.append(parameter)
        return parameters

    @property
    def provenance(self):
        """The provenance that is provided with the loaded profile.


        :returns: The provenance.
        :rtype: str
        """
        return self.minimum_needs['provenance']

    @property
    def root_directory(self):
        """Get the home root directory

        :returns: root directory
        :rtype: QString
        """
        if self._root_directory is None or self._root_directory == '':
            try:
                # noinspection PyArgumentList
                self._root_directory = QgsApplication.qgisSettingsDirPath()
            except NameError:
                # This only happens when running only one test on its own
                self._root_directory = None
            if self._root_directory is None or self._root_directory == '':
                self._root_directory = "%s/.qgis2" % (os.environ['HOME'])
        return self._root_directory

    @staticmethod
    def format_sentence(sentence, resource):
        """Populate the placeholders in the sentence.

        :param sentence: The sentence with placeholder keywords.
        :type sentence: basestring, str

        :param resource: The resource to be placed into the sentence.
        :type resource: dict

        :returns: The formatted sentence.
        :rtype: basestring
        """
        sentence = sentence.split('{{')
        updated_sentence = sentence[0].rstrip()
        for part in sentence[1:]:
            replace, keep = part.split('}}')
            replace = replace.strip()
            updated_sentence = "%s %s%s" % (
                updated_sentence,
                resource[replace],
                keep
            )
        return updated_sentence
