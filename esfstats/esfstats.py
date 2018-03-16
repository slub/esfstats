#!/usr/bin/python3
# -*- coding: utf-8 -*-
import argparse
import collections

from elasticsearch import Elasticsearch


def traverse(dict_or_list, fieldpath=None):
    if fieldpath is None:
        fieldpath = []
    if isinstance(dict_or_list, dict):
        if "properties" in dict_or_list:
            dict_or_list = dict_or_list["properties"]
        iterator = dict_or_list.items()
    else:
        iterator = enumerate(dict_or_list)
    for k, v in iterator:
        yield fieldpath + [k], v
        if isinstance(v, (dict, list)):
            if "fields" not in v and "type" not in v:
                for k1, v1 in traverse(v, fieldpath + [k]):
                    yield k1, v1


def run():
    parser = argparse.ArgumentParser(description='return field statistics of an elasticsearch index')
    parser.add_argument('-host', type=str,
                        help='hostname or IP address of the elasticsearch instance to use, default is localhost.')
    parser.add_argument('-port', type=int, help='port of the elasticsearch instance to use, default is 9200.')
    parser.add_argument('-index', type=str, help='elasticsearch index to use')
    parser.add_argument('-type', type=str, help='elasticsearch index type to use')
    parser.add_argument('-marc', action="store_true", help='ignore MARC indicator')
    args = parser.parse_args()
    if args.host is None:
        args.host = 'localhost'
    if args.port is None:
        args.port = 9200

    es = Elasticsearch([{'host': args.host}], port=args.port)
    mapping = es.indices.get_mapping(index=args.index, doc_type=args.type)[args.index]["mappings"][args.type]
    stats = dict()
    for path, node in traverse(mapping):
        fullpath = str()
        for field in path:
            fullpath = fullpath + "." + field
        fullpath = fullpath[1:]
        if args.marc:
            fullpath = fullpath[:3] + ".*." + fullpath[-1:]
        fieldexistingresponse = es.search(
            index=args.index,
            doc_type=args.type,
            body={"query": {"bool": {"must": [{"exists": {"field": fullpath}}]}}},
            size=0
        )
        fullpathkeyword = fullpath + ".keyword"
        fieldcardinalityresponse = es.search(
            index=args.index,
            doc_type=args.type,
            body={"aggs": {"type_count": {"cardinality": {"field": fullpathkeyword, "precision_threshold": 40000}}}},
            size=0
        )
        fieldvaluecountresponse = es.search(
            index=args.index,
            doc_type=args.type,
            body={"aggs": {"types_count": {"value_count": {"field": fullpathkeyword}}}},
            size=0
        )
        stats[fullpath] = (
            fieldexistingresponse['hits']['total'],
            fieldcardinalityresponse['aggregations']['type_count']['value'],
            fieldvaluecountresponse['aggregations']['types_count']['value']
        )
        hitcount = es.search(
            index=args.index,
            doc_type=args.type,
            body={},
            size=0
        )['hits']['total']

    print(
        '{:11s}|{:6s}|{:11s}|{:6s}|{:11s}|{:15s}|{:40s}'.format("existing", "%", "notexisting", "!%", "occurrence",
                                                                "unique (appr.)", "field name"))
    print("-----------|------|-----------|------|-----------|---------------|----------------------------------------")
    sortedstats = collections.OrderedDict(sorted(stats.items()))

    for key, value in sortedstats.items():
        fieldexistingcount = value[0]
        fieldcardinality = value[1]
        fieldvaluecount = value[2]

        keyreplaced = key.replace(u'\ufeff', '')
        keyencoded = keyreplaced.encode('utf-8')
        fieldexistingcountreplaced = str(fieldexistingcount).replace(u'\ufeff', '')
        fieldexistingcountencoded = fieldexistingcountreplaced.encode('utf-8')

        existing = fieldexistingcountencoded.decode('utf-8')
        existingpercentage = (float(fieldexistingcount) / float(hitcount)) * 100
        notexisting = str(hitcount - int(fieldexistingcount))
        notexistingpercentage = (float(notexisting) / float(hitcount)) * 100
        occurrence = str(fieldvaluecount)
        unique = str(fieldcardinality)
        fieldname = keyencoded.decode('utf-8').replace(".", " > ")

        print('{:>11s}|{:>6.2f}|{:>11s}|{:>6.2f}|{:>11s}|{:>15s}| {:40s}'.format(existing,
                                                                                 existingpercentage,
                                                                                 notexisting,
                                                                                 notexistingpercentage,
                                                                                 occurrence,
                                                                                 unique,
                                                                                 '"' + fieldname + '"'))


if __name__ == "__main__":
    run()
