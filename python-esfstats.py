#!/usr/bin/python
# -*- coding: utf-8 -*-
from datetime import datetime
from elasticsearch import Elasticsearch
import collections
import json
from pprint import pprint
import argparse
import sys

stats = dict()

def traverse(obj,path):
    global stats
    if isinstance(obj, dict):
        for key, value in obj.iteritems():
            path=path+"_"+key
            traverse(value,path)
    elif isinstance(obj, list):
        for value in obj:
            traverse(value,path)
    else:
        if args.marc==True:
            if path[:1]!='_':
                marcpath=path[:3]+" "+path[-1:]
                path = marcpath
        if path not in stats:
            stats[path]=0
        if path in stats:
            stats[path]+=1
        
if __name__ == "__main__":
    parser=argparse.ArgumentParser(description='return field statistics of an ElasticSearch Search Index')
    parser.add_argument('-host',type=str,help='hostname or IP-Address of the ElasticSearch-node to use, default is localhost.')
    parser.add_argument('-port',type=int,help='Port of the ElasticSearch-node to use, default is 9200.')
    parser.add_argument('-index',type=str,help='ElasticSearch Search Index to use')
    parser.add_argument('-type',type=str,help='ElasticSearch Search Index Type to use')
    parser.add_argument('-marc',action="store_true",help='Ignore Marc Indicator')
    args=parser.parse_args()
    if args.host is None:
        args.host='localhost'
    if args.port is None:
        args.port=9200
    es=Elasticsearch([{'host':args.host}],port=args.port)  
    page = es.search(
      index = args.index,
      doc_type = args.type,
      scroll = '2m',
      size = 1000,
      body = {},
      _source=True)
    sid = page['_scroll_id']
    scroll_size = page['hits']['total']
    
    # Start scrolling
    hitcount=0
    while (scroll_size > 0):
      pages = es.scroll(scroll_id = sid, scroll='2m')
      sid = pages['_scroll_id']
      scroll_size = len(pages['hits']['hits'])
      for hits in pages['hits']['hits']:
        hitcount+=1
        for field in hits['_source']:
            traverse(hits['_source'][field],field)
    print '{:50s}|{:14s}|{:14s}'.format("field name","exist-count","notexistcount")
    print "--------------------------------------------------|--------------|-------------"
    sortedstats=collections.OrderedDict(sorted(stats.items()))
    for key, value in sortedstats.iteritems():
        print '{:50s}|{:9s} {:3s}%|{:14s}'.format(str(key),str(value),str(int((float(value)/float(hitcount))*100)),str(hitcount-int(value)))
