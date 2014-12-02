#! /usr/bin/env python

import datetime
import hashlib
import json
import requests
import xml.etree.ElementTree as ET
from itertools import groupby
from operator import itemgetter
from rdflib import Graph, URIRef
from rdflib.namespace import Namespace, RDFS, SKOS, FOAF, XSD
from rdflib.term import bind
from sys import stderr
from time import sleep
from urllib import urlopen, quote_plus

NSS = { 'atom':'http://www.w3.org/2005/Atom',
        'zapi':'http://zotero.org/ns/api',
        'x':'http://www.w3.org/1999/xhtml' }
DC = Namespace('http://purl.org/dc/terms/')
SCH = Namespace('http://schema.org/')

def yearmonth2date(ym):
    y,m = [ int(x) for x in ym.split('-') ]
    return datetime.date(y,m,1)

def date2yearmonth(d):
    return date.year + '-' + date.month

bind(XSD.gYearMonth, datetime.date, yearmonth2date, date2yearmonth)

def allbut(unwanted, d):
    return { k:v for k,v in d.iteritems() if not k in unwanted }

def entry2dict(entry):
    rows = entry.iterfind('.//x:tr', NSS) 
    kfun = lambda x: x[0]
    items = [ (row.attrib['class'], row.find('x:td', NSS).text)
              for row in rows ]
    return dict([(k, [ x[1] for x in g ]) 
                 for k,g in groupby(sorted(items, key=kfun), kfun) ])

def load_graph(url):
    r = None
    while True:
        r = requests.get(url, headers={
            'accept':'text/turtle', 'user-agent':'curl/7.30.0'})
        if r.status_code == 200: break
        sleep(3)
    g = Graph()
    g.parse(data=r.text, format='turtle')
    return g

def label(g, s):
    return g.preferredLabel(s, labelProperties=(
        FOAF.name, SCH.name, DC.title, SKOS.prefLabel, RDFS.label))[0][1].value

def generic_metadata(e):
    o = entry2dict(e)
    metadata = { 'title': e.find('atom:title', NSS).text,
                 'creators': [ { 'name': name } for name in o['creator'] ] }
    year = e.find('zapi:year', NSS)
    if year is not None:
        metadata['yearPublished'] = int(year.text)
    if 'url' in o:
        assert len(o['url']) == 1
        metadata['url'] = o['url'][0]
    if 'abstractNote' in o:
        assert len(o['abstractNote']) == 1
        metadata['abstract'] = o['abstractNote'][0]
    if 'accessDate' in o:
        assert len(o['accessDate']) == 1
        metadata['dateAccessed'] = o['accessDate'][0][0:10]
    return metadata

def article_metadata(e):
    o = entry2dict(e)
    if not 'DOI' in o or len(o['DOI']) == 0:
        print >> stderr, 'no DOI for ' + e.find('atom:id', NSS).text
        try:
            # weird Italian journals catalogued as books
            return book_metadata(e)
        except:
            return generic_metadata(e)
    url = 'http://dx.doi.org/' + o['DOI'][0]
    g = load_graph(url)
    article = URIRef(url)
    creators = list(g[article:DC.creator])
    if len(creators) == 0:
        raise Exception('no creators for ' + e.find('atom:id', NSS).text)
    return { '@id': url,
             'title': label(g, article),
             'yearPublished': g.value(article, DC.date).value.year,
             'creators': [ { '@id': str(uri), 'name': label(g, uri) }
                           for uri in creators ] }
def book_metadata(e):
    o = entry2dict(e)
    if not 'url' in o:
        raise Exception('missing URL for ' + e.find('atom:id', NSS).text)
    urls = [ u for u in o['url'] if u.startswith('http://www.worldcat.org/') ]
    if len(urls) == 0:
        raise Exception('no WorldCat URL for ' + e.find('atom:id', NSS).text)
    url = urls[0]
    g = load_graph(url)
    book = URIRef(url)
    creators = list(g[book:SCH.creator])
    contributors = list(g[book:SCH.contributor])
    editors = list(g[book:SCH.editor])
    authors = list(g[book:SCH.author])
    if len(creators) + len(contributors) + len(editors) + len(authors) == 0:
        raise Exception(
            'no creators or contributors from:\n' + url)
    o = { '@id': url,
          'title': label(g, book),
          'yearPublished': int(g.value(book, SCH.datePublished).value) }
    if len(creators) > 0:
        o['creators'] = [ { '@id': str(uri), 'name': label(g, uri) }
                          for uri in creators ]
    if len(contributors) > 0:
        o['contributors'] = [ { '@id': str(uri), 'name': label(g, uri) }
                              for uri in contributors ]
    if len(editors) > 0:
        # treat editors as contributors
        contributors = o.setdefault('contributors', [])
        contributors += [ { '@id': str(uri), 'name': label(g, uri) }
                          for uri in editors ]
    if len(authors) > 0:
        # treat authors as creators
        creators = o.setdefault('creators', [])
        creators += [ { '@id': str(uri), 'name': label(g, uri) }
                          for uri in authors ]
    return o

def booksection_metadata(e):
    o = allbut('yearPublished', allbut(('url',), generic_metadata(e)))
    o['partOf'] = book_metadata(e)
    return o

def index(array):
    return { o['id']: o for o in array }

def get_source_data(url):
    handlers = {
        'book'          : book_metadata,
        'bookSection'   : booksection_metadata,
        'document'      : generic_metadata,
        'journalArticle': article_metadata,
        'webpage'       : generic_metadata,
    }
    root = ET.parse(urlopen(url)).getroot()
    return dict([ (e.find('atom:id', NSS).text,
                   handlers[e.find('zapi:itemType', NSS).text](e)) 
                  for e in root.iterfind('./atom:entry', NSS) ])

def make_source_dict(sources, key, group):
    d = { 'id': ('http://perio.do/temporary/' + hashlib.md5(key).hexdigest()),
          'source': sources[key], 
          'definitions': index([ allbut(('source','sourceId'), item)
                                 for item in group ]) }

    source_ids = set([ item['sourceId']
                       for item in group if 'sourceId' in item ])
    if len(source_ids) > 1:
        raise Exception("too many source IDs for: " + key)
    if len(source_ids) == 1:
        d['sameAs'] = source_ids.pop()

    locators = [ item['locationInSource']
                 for item in group if 'locationInSource' in item ]
    if len(locators) == len(group) and len(set(locators)) == 1:
        d['source'] = { 'partOf': d['source'],
                        'locator': locators[0] }
        for v in d['definitions'].values():
            if 'locationInSource' in v:
                del v['locationInSource']
    else:
        for v in d['definitions'].values():
            if 'locationInSource' in v:
                if not '@id' in d['source']:
                    print >> stderr, "Locators: {}".format(set(locators))
                    raise Exception('no @id for: {}'.format(key))
                v['source'] = {
                    'partOf': d['source']['@id'],
                    'locator': v.pop('locationInSource')
                }

    for v in d['definitions'].values():
        if 'url' in v:
            v['url'] = quote_plus(v['url'])
                
    return d

def group_by_source(sources, items):
    kfun = itemgetter('source')
    return index([ make_source_dict(sources, key, list(group)) 
                   for key, group in groupby(sorted(items, key=kfun), kfun) ])

def keys_of(d):
    for k1,v in d.items():
        yield k1
        if isinstance(v, dict):
            for k2 in keys_of(v):
                yield k2

def verify_context(d):
    missing = ( set(keys_of(allbut(('@context',), d)))
                - set(d['@context'].keys()) )
    for m in sorted(missing):
        if m.startswith('@'): continue
        if m.startswith('http://'): continue
        if m in ("als-latn",
                 "eng-latn",
                 "fra-latn",
                 "ita-latn",
                 "nld-latn",
                 "spa-latn",
                 "swe-latn",
                 "ukr-cyrl"): continue
        print >> stderr, 'Context is missing entry for "{}"'.format(m)
    
data_in = json.load(open('in.json'))
context = data_in['@context']
sources = get_source_data(
    'https://api.zotero.org/groups/269098/items/top?start=0&limit=1000')
data_out = { '@context': data_in['@context'], 
             'periodCollections': 
             group_by_source(sources, data_in['definitions'].values()) }

verify_context(data_out)

print json.dumps(data_out)

  




