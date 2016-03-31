# coding=utf-8
"""Help text for the extent selector dialog."""

from safe.utilities.i18n import tr
from safe import messaging as m
from safe.messaging import styles

INFO_STYLE = styles.INFO_STYLE

__author__ = 'ismailsunni'


def extent_selector_help():
    """Help message for extent selector dialog.

    .. versionadded:: 3.2.1

    :returns: A message object containing helpful information.
    :rtype: messaging.message.Message
    """

    message = m.Message()
    message.add(m.Brand())
    message.add(heading())
    message.add(content())
    return message


def heading():
    """Helper method that returns just the header.

    This method was added so that the text could be reused in the
    other contexts.

    .. versionadded:: 3.2.2

    :returns: A heading object.
    :rtype: safe.messaging.heading.Heading
    """
    message = m.Heading(tr('Extent selector help'), **INFO_STYLE)
    return message


def content():
    """Helper method that returns just the content.

    This method was added so that the text could be reused in the
    dock_help module.

    .. versionadded:: 3.2.2

    :returns: A message object without brand element.
    :rtype: safe.messaging.message.Message
    """
    message = m.Message()
    paragraph = m.Paragraph(tr(
        'This tool allows you to specify which geographical region should be '
        'used for your analysis.'))
    message.add(paragraph)
    header = m.Heading(tr('Use intersection of hazard and exposure layers'),
                       **INFO_STYLE)
    message.add(header)
    paragraph = m.Paragraph(tr(
        'The largest area that can be analysed is the intersection of the '
        'hazard and exposure layers you have added. To choose this option, '
        'click \'Use intersection of hazard and exposure layers\'. '))
    message.add(paragraph)
    paragraph = m.Paragraph(tr(
        'Sometimes it is more useful to analyse a smaller area. This could be '
        'to reduce processing time (smaller areas with process faster) or '
        'because information is only needed in a certain area (e.g. if a '
        'district only wants information for their district, not for the '
        'entire city). If you want to analyse a smaller area, there are a few '
        'different ways to do this.'))
    message.add(paragraph)
    header = m.Heading(tr('Use intersection of hazard, exposure and current '
                          'view extent'), **INFO_STYLE)
    message.add(header)
    paragraph = m.Paragraph(tr(
        'If you wish to conduct the analysis on the area currently shown in '
        'the window, you can set the analysis area to \'Use intersection of '
        'hazard, exposure and current view extent\'. '))
    message.add(paragraph)
    header = m.Heading(tr('Use intersection of hazard, exposure and this '
                          'bookmark'), **INFO_STYLE)
    message.add(header)
    paragraph = m.Paragraph(tr(
        'You can also use one of your QGIS bookmarks to set the region. This '
        'option will be greyed out if you have no bookmarks. MORE ON '
        'BOOKMARKS HERE '))
    message.add(paragraph)
    paragraph = m.Paragraph(tr(
        'If you enable the \'Toggle scenario outlines\' tool on the '
        'InaSAFE toolbar, your user defined extent will be shown on '
        'the map as a blue rectangle.'))
    message.add(paragraph)
    header = m.Heading(tr('Use intersection of hazard, exposure and this '
                          'bounding box'), **INFO_STYLE)
    message.add(header)
    paragraph = m.Paragraph(tr(
        'You can also choose the analysis area interactively by clicking '
        '\'Use intersection of hazard, exposure and this bounding box\'. This '
        'will allow you to click \'Drag on map\' which will temporarily hide '
        'this window and allow you to drag a rectangle on the map. After you '
        'have finished dragging the rectangle, this window will reappear with '
        'values in the North, South, East and West boxes. '))
    message.add(paragraph)
    paragraph = m.Paragraph(tr(
        'Alternatively you can enter the coordinates directly into the boxes '
        'once the \'Use intersection of hazard, exposure and this bounding '
        'box\' is selected (using the same coordinate reference system, or '
        'CRS, as the map is currently set to).'))
    message.add(paragraph)


    return message
