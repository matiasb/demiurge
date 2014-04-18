# -*- coding: utf-8 -*-

import unittest

from mock import patch

import demiurge


HTML_SAMPLE = """
<html>
    <body>
        <p class="p_with_link">
            Some text.
            <a class="link" href="http://github.com/matiasb">Link text.</a>
        </p>
        <p class="p_with_link">
            <a class="link" href="http://github.com/matiasb/demiurge">Another link.</a>
        </p>
    </body>
</html>
"""


class TestItem(demiurge.Item):
    label = demiurge.TextField(selector='.link')
    url = demiurge.AttributeValueField(selector='.link', attr='href')

    class Meta:
        base_url = 'http://localhost'
        selector = "p.p_with_link"
        extra_attribute = 'value'


class TestDemiurge(unittest.TestCase):

    def setUp(self):
        super(TestDemiurge, self).setUp()
        patcher = patch('demiurge.demiurge.pyquery.pyquery.url_opener')
        self.addCleanup(patcher.stop)
        self.mock_opener = patcher.start()
        self.mock_opener.return_value = HTML_SAMPLE

    @patch('demiurge.demiurge.pyquery.PyQuery')
    def test_one(self, mock_pq):
        item = TestItem.one()

        # extra Meta attributes are passed into PyQuery init
        mock_pq.assert_called_once_with(
            url='http://localhost', extra_attribute='value')

    def test_one(self):
        item = TestItem.one()

        self.assertIsNotNone(item)
        self.assertEqual(item.label, 'Link text.')
        self.assertEqual(item.url, 'http://github.com/matiasb')

    def test_one_with_index(self):
        item = TestItem.one(index=1)

        self.assertIsNotNone(item)
        self.assertEqual(item.label, 'Another link.')
        self.assertEqual(item.url, 'http://github.com/matiasb/demiurge')

    def test_all(self):
        items = TestItem.all()

        self.assertEqual(len(items), 2)
        self.assertEqual(items[0].label, 'Link text.')
        self.assertEqual(items[0].url, 'http://github.com/matiasb')
        self.assertEqual(items[1].label, 'Another link.')
        self.assertEqual(items[1].url, 'http://github.com/matiasb/demiurge')

    def test_one_not_found(self):
        self.mock_opener.return_value = "<html></html>"

        with self.assertRaises(demiurge.ItemDoesNotExist):
            TestItem.one()

    def test_all_not_found(self):
        self.mock_opener.return_value = "<html></html>"

        self.assertEqual(TestItem.all(), [])

    def test_all_from(self):
        items = TestItem.all_from(HTML_SAMPLE)

        self.assertEqual(len(items), 2)
        self.assertEqual(items[0].label, 'Link text.')
        self.assertEqual(items[0].url, 'http://github.com/matiasb')
        self.assertEqual(items[1].label, 'Another link.')
        self.assertEqual(items[1].url, 'http://github.com/matiasb/demiurge')

    def test_item_html(self):
        item = TestItem.one()

        expected = (
            '\n            Some text.\n            <a class="link"'
            ' href="http://github.com/matiasb">Link text.</a>\n        '
        )
        self.assertIsNotNone(item)
        self.assertEqual(item.html, expected)


if __name__ == '__main__':
    unittest.main()
