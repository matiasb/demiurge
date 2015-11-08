demiurge
========

PyQuery-based scraping micro-framework.
Supports Python 2.x and 3.x.

[![Build Status](https://travis-ci.org/matiasb/demiurge.png?branch=master)](https://travis-ci.org/matiasb/demiurge)

Documentation: http://demiurge.readthedocs.org


Installing demiurge
-------------------

```
$ pip install demiurge
```

Quick start
-----------

Define items to be scraped using a declarative (Django-inspired) syntax:

```python
import demiurge

class TorrentDetails(demiurge.Item):
    label = demiurge.TextField(selector='strong')
    value = demiurge.TextField()

    def clean_value(self, value):
        unlabel = value[value.find(':') + 1:]
        return unlabel.strip()

    class Meta:
        selector = 'div#specifications p'

class Torrent(demiurge.Item):
    url = demiurge.AttributeValueField(
        selector='td:eq(2) a:eq(1)', attr='href')
    name = demiurge.TextField(selector='td:eq(2) a:eq(2)')
    size = demiurge.TextField(selector='td:eq(3)')
    details = demiurge.RelatedItem(
        TorrentDetails, selector='td:eq(2) a:eq(2)', attr='href')

    class Meta:
        selector = 'table.maintable:gt(0) tr:gt(0)'
        base_url = 'http://www.mininova.org'


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
Ubuntu 7.10 Desktop Live CD 695.81 MB
Super Ubuntu 2008.09 - VMware image 871.95 MB
Portable Ubuntu 9.10 for Windows 559.78 MB
...

>>> t = Torrent.one('/search/ubuntu/seeds')
>>> for detail in t.details:
...     print detail.label, detail.value
... 
Category: Software > GNU/Linux
Total size: 695.81 megabyte
Added: 2467 days ago by Distribution
Share ratio: 17 seeds, 2 leechers
Last updated: 35 minutes ago
Downloads: 29,085
```

See documentation for details: http://demiurge.readthedocs.org


Why *demiurge*?
---------------

Plato, as the speaker Timaeus, refers to the Demiurge frequently in the Socratic
dialogue Timaeus, c. 360 BC. The main character refers to the Demiurge as the
entity who "fashioned and shaped" the material world. Timaeus describes the
Demiurge as unreservedly benevolent, and hence desirous of a world as good as
possible. The world remains imperfect, however, because the Demiurge created
the world out of a chaotic, indeterminate non-being.

http://en.wikipedia.org/wiki/Demiurge


Contributors
------------

 - Martín Gaitán (@mgaitan)
