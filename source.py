#! /usr/bin/env python

import datetime
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
from urllib import urlopen

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
    return { k:v for k,v in d.iteritems() if not k == unwanted }

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
                 'yearPublished': e.find('zapi:year', NSS).text,
                 'creators': [ { 'name': name } for name in o['creator'] ] }
    if 'url' in o: metadata['url'] = o['url']
    return metadata

def article_metadata(e):
    o = entry2dict(e)
    if not 'DOI' in o or len(o['DOI']) == 0:
        print >> stderr, 'no DOI for ' + e.find('atom:id', NSS).text
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
    if len(creators) + len(contributors) == 0:
        raise Exception(
            'no creators or contributors for ' + e.find('atom:id', NSS).text)
    o = { '@id': url,
          'title': label(g, book),
          'yearPublished': int(g.value(book, SCH.datePublished).value) }
    if len(creators) > 0:
        o['creators'] = [ { '@id': str(uri), 'name': label(g, uri) }
                          for uri in creators ]
    if len(contributors) > 0:
        o['contributors'] = [ { '@id': str(uri), 'name': label(g, uri) }
                              for uri in contributors ]
    return o

def booksection_metadata(e):
    o = allbut('url', generic_metadata(e))
    o['partOf'] = book_metadata(e)
    return o

def get_source_data(url):
    handlers = {
        'book': book_metadata,
        'bookSection': booksection_metadata,
        'journalArticle': article_metadata,
    }
    root = ET.parse(urlopen(url)).getroot()
    return dict([ (e.find('atom:id', NSS).text,
                   handlers[e.find('zapi:itemType', NSS).text](e)) 
                  for e in root.iterfind('./atom:entry', NSS) ])

def group_by_source(sources, items):
    kfun = itemgetter('source')
    return [ { 'source': sources[key], 
               'definitions':[ allbut('source', item) for item in group ] } 
             for key, group in groupby(sorted(items, key=kfun), kfun) ]

    
o = json.load(open('data.json'))
context = o['@context']
context.update({ 
    'definitions': { '@reverse': SKOS.inScheme },
    'partOf': DC.isPartOf,
    'title': DC.title,
    'creators': DC.creator,
    'contributors': DC.contributor,
    'name': FOAF.name,
    'yearPublished': { '@id': DC.date, '@type': XSD.gYear },
    'url': FOAF.homepage,
})
sources = get_source_data(
    'https://api.zotero.org/groups/269098/items/top?start=0&limit=100')
print json.dumps({ '@context': context, 
                   '@graph': group_by_source(sources, o['@graph']) })
  




