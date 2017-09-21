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
    if path[0]=='_':
       return
    path=path.replace("_properties","");
    path=path.replace("_keyword","");
    path=path.replace("_ignore","");
    path=path.replace("_fields","");
    path=path.replace("_above","");
    path=path.replace("_type","");
    
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
            if len(path)>3:
                if path[0]!='_':
                    marcpath=path[:3]+".*."+path[-1:]
                    path = marcpath
        if path not in stats:
            stats[path]=0
        
if __name__ == "__main__":
    parser=argparse.ArgumentParser(description='return field statistics of an ElasticSearch Search Index')
    parser.add_argument('-host',type=str,help='hostname or IP-Address of the ElasticSearch-node to use, default is localhost.')
    parser.add_argument('-port',type=int,help='Port of the ElasticSearch-node to use, default is 9200.')
    parser.add_argument('-index',type=str,help='ElasticSearch Search Index to use')
    parser.add_argument('-type',type=str,help='ElasticSearch Search Index Type to use')
    parser.add_argument('-marc',action="store_true",help='Marc')
    args=parser.parse_args()
    if args.host is None:
        args.host='localhost'
    if args.port is None:
        args.port=9200
    es=Elasticsearch([{'host':args.host}],port=args.port)  
    mapping = es.indices.get_mapping(index=args.index,doc_type=args.type)[args.index]
    for field in mapping["mappings"][args.type]["properties"]:
        traverse(mapping["mappings"][args.type]["properties"][field],field)
    for key, val in stats.iteritems():
        page = es.search(
            index = args.index,
            doc_type = args.type,
            body = {"query":{"bool":{"must":[{"exists": {"field": key}}]}}},
            size=0
            )
        stats[key]=page['hits']['total']
    hitcount=es.search(
            index = args.index,
            doc_type = args.type,
            body = {},
            size=0
            )['hits']['total']
    print '{:40s}|{:11s}|{:3s}|{:14s}'.format("field name","existing","%","notexisting")
    print "----------------------------------------|-----------|---|-----------"
    sortedstats=collections.OrderedDict(sorted(stats.items()))
    for key, value in sortedstats.iteritems():
        print '{:40s}|{:>11s}|{:>3s}|{:1>4s}'.format(str(key),str(value),str(int((float(value)/float(hitcount))*100)),str(hitcount-int(value)))
