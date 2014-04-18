demiurge
========

PyQuery-based scraping micro-framework.  
Supports Python 2.x and 3.x.

[![Build Status](https://travis-ci.org/matiasb/demiurge.png?branch=master)](https://travis-ci.org/matiasb/demiurge)


Installing demiurge
-------------------

    $ pip install demiurge


Quick start
-----------

    >>> import demiurge

You can define items to be scraped using a declarative (Django-inspired) syntax:

    >>> class Torrent(demiurge.Item):
    ...     url = demiurge.AttributeValueField(selector='td:eq(2) a:eq(1)', attr='href')
    ...     name = demiurge.TextField(selector='td:eq(2) a:eq(2)')
    ...     size = demiurge.TextField(selector='td:eq(3)')
    ...     class Meta:
    ...         selector = 'table.maintable:gt(0) tr:gt(0)'
    ...         base_url = 'http://www.mininova.org'
    ... 

At the moment, there is only two possible fields, *TextField* and
*AttributeValueField*. A *TextField* expects an optional *selector* argument,
meanwhile *AttributeValueField* possible arguments are *selector* and *attr*.

*selector* specifies the PyQuery selector for the element,
relative to the *Item* element (determined by the Meta *selector* attribute). If
not specified, the current *Item* element is assumed.

On the other hand, *attr* parameter allows to retrieve an element
attribute value instead of its text content.

In the example above, the *Item* selector is any row but not the first one, from
the table with css class *maintable* (also ignoring the first ocurrence,
sponsored results).

Each field selector is relative to the *Item* element (in this case, a table row).
Then, *name* refers to the second anchor in the second cell.

Once you defined your items, there are a couple of useful methods you can use,
both expecting as argument a relative path to the *Item* *base\_url* if it was
defined in the *Item.Meta* class, or a full URL (if *base\_url* was not specified):

    >>> t = Torrent.one('/search/ubuntu/seeds')
    >>> t.name
    'Ubuntu 7.10 Desktop Live CD'
    >>> t.size
    u'695.81\xa0MB'
    >>> t.url
    '/get/1053846'
    >>> t.html
    u'<td>19\xa0Dec\xa007</td><td><a href="/cat/7">Software</a></td><td>...'

    >>> results = Torrent.all('/search/ubuntu/seeds')
    >>> len(results)
    116
    >>> for t in results[:3]:
    ...     print t.name, t.size
    ... 
    Ubuntu 7.10 Desktop Live CD 695.81 MB
    Super Ubuntu 2008.09 - VMware image 871.95 MB
    Portable Ubuntu 9.10 for Windows 559.78 MB
    ...

Also, any extra attributes defined in the *Item.Meta* class will be passed
to PyQuery when doing the URL request (i.e. you could add, for example,
*encoding* or *method*; if python-requests is available, there is a bunch of
extra parameters you could use: *auth*, *data*, *headers*, *verify*, *cert*,
*config*, *hooks*, *proxies*).

Alternatively, there is an *all\_from* method that will retrieve all items from
a PyQuery object created from the given arguments (i.e. it will directly pass
all specified parameters to PyQuery and scrap items from there).


Why *demiurge*?
---------------

Plato, as the speaker Timaeus, refers to the Demiurge frequently in the Socratic
dialogue Timaeus, c. 360 BC. The main character refers to the Demiurge as the
entity who "fashioned and shaped" the material world. Timaeus describes the
Demiurge as unreservedly benevolent, and hence desirous of a world as good as
possible. The world remains imperfect, however, because the Demiurge created
the world out of a chaotic, indeterminate non-being.

http://en.wikipedia.org/wiki/Demiurge


To Do
-----

- Add real documentation
- Add more/extra fields
