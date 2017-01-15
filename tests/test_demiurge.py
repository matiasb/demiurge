# -*- coding: utf-8 -*-

import unittest

from mock import patch

import demiurge


HTML_INDEX_RELATIVE = """
<html>
    <body>
        <h1>Second page</h1>
        <div><a class="link" href="links">Link text.</a></div>
        <div><a class="next" href="?page=3">next</a></div>
    </body>
</html>
"""

HTML_INDEX_ABSOLUTE = """
<html>
    <body>
        <h1>First page</h1>
        <div>
            <a class="link" href="http://another-server/links">Link text.</a>
        </div>
        <div><a class="next" href="?page=2">next</a></div>
    </body>
</html>
"""


HTML_SAMPLE = """
<html>
    <body>
        <div class="section">
        </div>
        <div class="section">
            <p class="p_with_link">
                Some text.
                <a class="link" href="http://github.com/matiasb">Link text.</a>
            </p>
            <p class="p_with_link">
                <a class="link" href="http://github.com/matiasb/demiurge">
                    Another link.</a>
            </p>
        </div>
        <div class="pagination">
            <a class="page" href="?page=2">Page 2</a>
            <a class="page" href="?page=3">Page 3</a>
        </div>
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


class TestItemNoSelector(demiurge.Item):
    class Meta:
        base_url = 'http://localhost'


class TestItemWithClean(demiurge.Item):
    label = demiurge.TextField(selector='.link')

    def clean_label(self, value):
        return value.upper()

    class Meta:
        base_url = 'http://localhost'
        selector = 'p'


class TestItemWithFieldCoercion(demiurge.Item):
    label = demiurge.TextField(selector='a.page', coerce=int)
    url = demiurge.AttributeValueField(
        selector='a.page', attr='href', coerce=bool)

    def clean_label(self, value):
        # remove the Page prefix
        return value[5:]

    class Meta:
        base_url = 'http://localhost'
        selector = 'div.pagination'


class TestIndexItem(demiurge.Item):
    title = demiurge.TextField(selector='h1')
    items_following_link = demiurge.RelatedItem(
        TestItem, selector='a.link', attr='href')
    next_page = demiurge.RelatedItem('self', selector='a.next', attr='href')

    class Meta:
        base_url = 'http://localhost'


class TestInnerItem(demiurge.Item):
    inner_items = demiurge.RelatedItem(TestItem)

    class Meta:
        base_url = 'http://localhost'
        selector = "div.section"


class TestDemiurge(unittest.TestCase):

    def setUp(self):
        super(TestDemiurge, self).setUp()
        patcher = patch('demiurge.demiurge.pyquery.pyquery.url_opener')
        self.addCleanup(patcher.stop)
        self.mock_opener = patcher.start()
        self.mock_opener.return_value = HTML_SAMPLE

    def test_extra_meta_values(self):
        TestItem.one()

        # extra Meta attributes are passed to the opener
        self.mock_opener.assert_called_once_with(
            'http://localhost', {'extra_attribute': 'value'})

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
            '\n                Some text.\n                '
            '<a class="link" href="http://github.com/matiasb">'
            'Link text.</a>\n            '
        )
        self.assertIsNotNone(item)
        self.assertEqual(item.html, expected)

    def test_no_selector_uses_whole_html(self):
        self.mock_opener.return_value = "<html><body><p>body</p></body></html>"
        item = TestItemNoSelector.one()
        self.assertEqual(item.html, '<body><p>body</p></body>')

    def test_item_clean(self):
        item = TestItemWithClean.one()
        self.assertEqual(item.label, 'LINK TEXT.')

    def test_item_field_coercion(self):
        item = TestItemWithFieldCoercion.one()
        self.assertEqual(item.label, 2)
        self.assertEqual(item.url, True)

    def test_relateditem_following_link(self):
        self.mock_opener.side_effect = [HTML_INDEX_RELATIVE, HTML_SAMPLE]

        index = TestIndexItem.one()
        calls = self.mock_opener.call_args_list
        self.assertEqual(len(calls), 1)

        links = index.items_following_link
        calls = self.mock_opener.call_args_list
        self.assertEqual(len(calls), 2)
        # second call follows relative link
        self.assertEqual(calls[1][0][0], 'http://localhost/links')

        self.assertEqual(len(links), 2)
        self.assertEqual(links[0].label, 'Link text.')
        self.assertEqual(links[0].url, 'http://github.com/matiasb')
        self.assertEqual(links[1].label, 'Another link.')
        self.assertEqual(links[1].url, 'http://github.com/matiasb/demiurge')

    def test_relateditem_following_absolute_link(self):
        self.mock_opener.side_effect = [HTML_INDEX_ABSOLUTE, HTML_SAMPLE]

        index = TestIndexItem.one()
        calls = self.mock_opener.call_args_list
        self.assertEqual(len(calls), 1)

        links = index.items_following_link
        calls = self.mock_opener.call_args_list
        self.assertEqual(len(calls), 2)
        # second call follows relative link
        self.assertEqual(calls[1][0][0], 'http://another-server/links')

        self.assertEqual(len(links), 2)
        self.assertEqual(links[0].label, 'Link text.')
        self.assertEqual(links[0].url, 'http://github.com/matiasb')
        self.assertEqual(links[1].label, 'Another link.')
        self.assertEqual(links[1].url, 'http://github.com/matiasb/demiurge')

    def test_relateditem_subitem(self):
        self.mock_opener.side_effect = [HTML_SAMPLE]

        parents = TestInnerItem.all()
        self.assertEqual(len(parents), 2)

        # first section, no links
        links = parents[0].inner_items
        self.assertEqual(len(links), 0)

        # second section, the links
        links = parents[1].inner_items
        self.assertEqual(len(links), 2)
        self.assertEqual(links[0].label, 'Link text.')
        self.assertEqual(links[0].url, 'http://github.com/matiasb')
        self.assertEqual(links[1].label, 'Another link.')
        self.assertEqual(links[1].url, 'http://github.com/matiasb/demiurge')

    def test_relateditem_with_self_reference(self):
        self.mock_opener.side_effect = [HTML_INDEX_ABSOLUTE,
                                        HTML_INDEX_RELATIVE]
        first_page = TestIndexItem.one()
        assert first_page.title == 'First page'
        next_page = first_page.next_page[0]
        self.assertIsInstance(next_page, TestIndexItem)
        self.assertEqual(next_page.title, 'Second page')
        self.assertIn('?page=3', next_page.html)

    def test_setting_relateditem_raises(self):
        self.mock_opener.side_effect = [HTML_SAMPLE]
        parents = TestInnerItem.all()
        first = parents[0]

        with self.assertRaises(AttributeError):
            first.inner_items = []


if __name__ == '__main__':
    unittest.main()
