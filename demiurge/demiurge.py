#-*- coding:utf-8 -*-

import sys

import pyquery


PY3 = sys.version_info[0] == 3

if PY3:
    from urllib.parse import urljoin
else:
    from urlparse import urljoin


def with_metaclass(meta, base=object):
    """Create a base class with a metaclass."""
    return meta("NewBase", (base,), {})


class BaseField(object):
    """Base demiurge field."""

    def clean(self, value):
        """Clean extracted value."""
        return value

    def get_value(self, pq):
        """Extract value from given PyQuery element."""
        raise NotImplementedError(
            "Custom fields have to implement this method")


class TextField(BaseField):
    """Simple text field.

    Extract text content from a tag given by 'selector'.
    'selector' is a pyquery supported selector; if not specified, the Item
    base element is used.

    """

    def __init__(self, selector=None, attr=None):
        super(TextField, self).__init__()
        self.selector = selector
        self.attr = attr

    def clean(self, value):
        value = super(TextField, self).clean(value)
        if value is not None:
            return value.strip()

    def get_value(self, pq):
        value = None

        tag = pq
        if self.selector is not None:
            tag = pq(self.selector).eq(0)

        if tag:
            value = tag.text()
        return value


class AttributeValueField(TextField):
    """Simple text field, getting an attribute value.

    Extract specific attribute value from a tag given by 'selector'.
    'selector' is a pyquery supported selector; if not specified, the Item
    base element is used.

    """

    def get_value(self, pq):
        value = None

        if self.selector is not None:
            tag = pq(self.selector).eq(0)
        else:
            tag = pq

        if tag and self.attr is not None:
            html_elem = tag[0]
            value = html_elem.get(self.attr)

        return value


def get_fields(bases, attrs):
    fields = [(field_name, attrs.pop(field_name)) for field_name, obj in
              list(attrs.items()) if isinstance(obj, BaseField)]
    # add inherited fields
    for base in bases[::-1]:
        if hasattr(base, '_fields'):
            fields = list(base._fields.items()) + fields
    return dict(fields)


class ItemOptions(object):
    """Meta options for an item."""

    DEMIURGE_VALUES = ('selector', 'base_url')

    def __init__(self, meta):
        self.selector = getattr(meta, 'selector', 'html')
        self.base_url = getattr(meta, 'base_url', '')
        attrs = getattr(meta, '__dict__', {})
        self._pyquery_kwargs = {}
        for attr, value in attrs.items():
            if (attr not in self.DEMIURGE_VALUES and not attr.startswith('_')):
                self._pyquery_kwargs[attr] = value


class ItemMeta(type):
    """Metaclass for a demiurge item."""

    def __new__(cls, name, bases, attrs):
        attrs['_fields'] = get_fields(bases, attrs)
        new_class = super(ItemMeta, cls).__new__(cls, name, bases, attrs)
        new_class._meta = ItemOptions(getattr(new_class, 'Meta', None))
        return new_class


class ItemDoesNotExist(Exception):
    """Item does not exist."""


class Item(with_metaclass(ItemMeta)):
    """Base class for any demiurge item."""

    def __init__(self, item=None):
        if item is None or not isinstance(item, pyquery.PyQuery):
            raise ValueError('PyQuery object expected')

        self._pq = item
        for field_name, field in self._fields.items():
            raw_value = field.get_value(self._pq)
            value = field.clean(raw_value)
            setattr(self, field_name, value)

    @property
    def html(self):
        """Original HTML snippet from which values where extracted."""
        return self._pq.html()

    @classmethod
    def _get_items(cls, *args, **kwargs):
        pq = pyquery.PyQuery(*args, **kwargs)
        items = pq.find(cls._meta.selector)
        return items

    @classmethod
    def all_from(cls, *args, **kwargs):
        """Query for items passing PyQuery args explicitly."""
        pq_items = cls._get_items(*args, **kwargs)
        return [cls(item=i) for i in pq_items.items()]

    @classmethod
    def one(cls, path='', index=0):
        """Return ocurrence (the first one, unless specified) of the item."""
        url = urljoin(cls._meta.base_url, path)
        pq_items = cls._get_items(url=url, **cls._meta._pyquery_kwargs)
        item = pq_items.eq(index)
        if not item:
            raise ItemDoesNotExist("%s not found" % cls.__name__)
        return cls(item=item)

    @classmethod
    def all(cls, path=''):
        """Return all ocurrences of the item."""
        url = urljoin(cls._meta.base_url, path)
        pq_items = cls._get_items(url=url, **cls._meta._pyquery_kwargs)
        return [cls(item=i) for i in pq_items.items()]
