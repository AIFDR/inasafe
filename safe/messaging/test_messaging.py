"""
InaSAFE Disaster risk assessment tool developed by AusAid - **Paragraph.**

Contact : ole.moller.nielsen@gmail.com

.. note:: This program is free software; you can redistribute it and/or modify
     it under the terms of the GNU General Public License as published by
     the Free Software Foundation; either version 2 of the License, or
     (at your option) any later version.
"""

__author__ = 'marco@opengis.ch'
__revision__ = '$Format:%H$'
__date__ = '27/05/2013'
__copyright__ = ('Copyright 2012, Australia Indonesia Facility for '
                 'Disaster Reduction')

import unittest
import os

from safe.messaging import Message, Text, EmphasizedText, ImportantText, Heading, Paragraph


class MessagingTest(unittest.TestCase):
    """Tests for creating and displaying messages
    """

    def setUp(self):
        os.environ['LANG'] = 'en'

    def tearDown(self):
        pass

    def test_text(self):
        """Tests Text messages are rendered correctly in plain text/html.
        """
        t1 = Text('FOO')
        t2 = Text('BAR')
        expected_res = 'FOO'

        res = t1.to_text()
        self.assertEqual(expected_res, res)

        t1.add(t2)
        expected_res = 'FOOBAR'
        res = t1.to_html()
        self.assertEqual(expected_res, res)

    def test_text_complex(self):
        """Tests Text messages are rendered correctly in plain text/html.
        """
        t1 = Text('FOO')
        ts = ImportantText('STRONG')
        t2 = Text(ts)
        t1.add(t2)
        expected_res = 'FOO*STRONG*'

        res = t1.to_text()
        self.assertEqual(expected_res, res)

    def test_heading(self):
        """Tests heading messages are rendered correctly in plain text/html.
        """
        h = Heading('FOO', -3)
        expected_res = '*FOO\n'
        res = h.to_text()
        self.assertEqual(expected_res, res)

        h = Heading('FOO', 8)
        expected_res = '********FOO\n'
        res = h.to_text()
        self.assertEqual(expected_res, res)

        expected_res = '<h6>FOO</h6>'
        res = h.to_html()
        self.assertEqual(expected_res, res)

    def test_paragraph(self):
        """Tests paragraphs are rendered correctly in plain text/html.
        """
        p = Paragraph('FOO')
        expected_res = '\nFOO\n'
        res = p.to_text()
        self.assertEqual(expected_res, res)

        expected_res = '<p>FOO</p>'
        res = p.to_html()
        self.assertEqual(expected_res, res)

    def test_message(self):
        """Tests high level messages are rendered correctly in plain text/html.
        """
        m1 = Message('FOO')
        expected_res = 'FOO\n'
        res = m1.to_text()
        self.assertEqual(expected_res, res)

        #TODO (MB) Check this double \n going on here
        m2 = Message(m1)
        expected_res = 'FOO\n\n'
        res = m2.to_text()
        self.assertEqual(expected_res, res)

        m3 = Message(Message('FOO'))
        m3.add(Message('BAR'))
        expected_res = 'FOO\n\nBAR\n\n'
        res = m3.to_text()
        self.assertEqual(expected_res, res)

    def test_complex_message(self):
        """Tests complex messages are rendered correctly in plain text/html
        """
        h1 = Heading('h1 title')
        h2 = Heading('h2 subtitle', 2)
        p1 = Paragraph('the quick brown fox jumps over the lazy dog')

        t1 = Text('this is a text, ')
        t1.add(Text('this is another text '))
        ts = ImportantText('and this is a strong text')
        t1.add(ts)
        t1.add(Text(' spaced text'))
        tp = Text('text for paragraph ')
        em = EmphasizedText('this is an emphasized paragraph text')
        tp.add(em)
        p2 = Paragraph(tp)

        m = Message()
        m.add(h1)
        m.add(h2)
        m.add(p1)
        m.add(t1)
        m.add(p2)

        expected_res = (
            '*h1 title\n\n'
            '**h2 subtitle\n\n'
            '\nthe quick brown fox jumps over the lazy dog\n\n'
            'this is a text, this is another text *and this is a strong text* '
            'spaced text\n'
            '\ntext for paragraph _this is an emphasized paragraph text_\n\n')

        res = m.to_text()
        self.assertEqual(expected_res, res)

        expected_res = (
            '<h1>h1 title</h1>\n'
            '<h2>h2 subtitle</h2>\n'
            '<p>the quick brown fox jumps over the lazy dog</p>\n'
            'this is a text, this is another text <strong>and this is a strong '
            'text</strong> spaced text\n'
            '<p>text for paragraph <em>this is an emphasized paragraph text'
            '</em></p>\n')
        res = m.to_html()
        self.assertEqual(expected_res, res)

if __name__ == '__main__':
    suite = unittest.makeSuite(MessagingTest, 'test')
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite)
