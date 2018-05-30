#!/usr/bin/python3
# -*- coding: utf-8 -*-
import argparse
import collections
import csv
import sys

from elasticsearch import Elasticsearch

EXISTING = 'existing'
EXISTING_PERCENTAGE = 'existing_percentage'
NOTEXISTING = 'notexisting'
NOTEXISTING_PERCENTAGE = 'notexisting_percentage'
OCCURRENCE = 'occurrence'
UNIQUE_APPR = 'unique_appr'
FIELD_NAME = 'field_name'


def get_header():
    return [EXISTING,
            EXISTING_PERCENTAGE,
            NOTEXISTING,
            NOTEXISTING_PERCENTAGE,
            OCCURRENCE,
            UNIQUE_APPR,
            FIELD_NAME]


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


def generate_field_statistics(statsmap, hitcount):
    field_statistics = []

    for key, value in statsmap:
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

        field_statistic = {EXISTING: existing,
                           EXISTING_PERCENTAGE: "{0:.2f}".format(existingpercentage),
                           NOTEXISTING: notexisting,
                           NOTEXISTING_PERCENTAGE: "{0:.2f}".format(notexistingpercentage),
                           OCCURRENCE: occurrence,
                           UNIQUE_APPR: unique,
                           FIELD_NAME: fieldname}

        field_statistics.append(field_statistic)

    return field_statistics


def simple_text_print(field_statistics):
    print('{:11s}|{:6s}|{:11s}|{:6s}|{:11s}|{:15s}|{:40s}'.format("existing", "%", "notexisting", "!%", "occurrence",
                                                                  "unique (appr.)", "field name"))
    print("-----------|------|-----------|------|-----------|---------------|----------------------------------------")

    for field_statistic in field_statistics:
        print('{:>11s}|{:>6.2f}|{:>11s}|{:>6.2f}|{:>11s}|{:>15s}| {:40s}'.format(field_statistic[EXISTING],
                                                                                 float(field_statistic[
                                                                                           EXISTING_PERCENTAGE]),
                                                                                 field_statistic[NOTEXISTING],
                                                                                 float(field_statistic[
                                                                                           NOTEXISTING_PERCENTAGE]),
                                                                                 field_statistic[OCCURRENCE],
                                                                                 field_statistic[UNIQUE_APPR],
                                                                                 '"' + field_statistic[
                                                                                     FIELD_NAME] + '"'))

def csv_print(field_statistics):
    header = get_header()
    with sys.stdout as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=header, dialect='unix')

        writer.writeheader()
        for field_statistic in field_statistics:
            writer.writerow(field_statistic)

def isint(num):
    try: 
        int(num)
        return True
    except:
        return False

def run():
    parser = argparse.ArgumentParser(prog='esfstats', description='return field statistics of an elasticsearch index',
                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    optional_arguments = parser._action_groups.pop()

    required_arguments = parser.add_argument_group('required arguments')
    required_arguments.add_argument('-index', type=str, help='elasticsearch index to use')
    required_arguments.add_argument('-type', type=str, help='elasticsearch index (document) type to use')
    
    
    required_arguments_or = parser.add_argument_group('or use: arguments')
    required_arguments_or.add_argument('-server',type=str,
                                    help="use http://host:port/index/type/id?pretty. overwrites host/port/index/id/pretty")

    optional_arguments.add_argument('-host', type=str, default='localhost',
                                    help='hostname or IP address of the elasticsearch instance to use')
    optional_arguments.add_argument('-port', type=int, default=9200,
                                    help='port of the elasticsearch instance to use')
    optional_arguments.add_argument('-marc', action="store_true", help='ignore MARC indicator')
    optional_arguments.add_argument('-csv-output', action="store_true",
                                    help='prints the output as pure CSV data (all values are quoted)',
                                    dest='csv_output')

    parser._action_groups.append(optional_arguments)

    args = parser.parse_args()
    
    if args.server:
        slashsplit=args.server.split("/")
        args.host=slashsplit[2].rsplit(":")[0]
        if isint(args.server.split(":")[2].rsplit("/")[0]):
            args.port=args.server.split(":")[2].split("/")[0]
        args.index=args.server.split("/")[3]
        if len(slashsplit)>4:
            args.type=slashsplit[4]
        if len(slashsplit)>5:
            if "?pretty" in args.server:
                args.pretty=True
                args.id=slashsplit[5].rsplit("?")[0]
            else:
                args.id=slashsplit[5]

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

    sortedstats = collections.OrderedDict(sorted(stats.items()))
    field_statistics = generate_field_statistics(sortedstats.items(), hitcount)

    if not args.csv_output:
        simple_text_print(field_statistics)
    else:
        csv_print(field_statistics)


if __name__ == "__main__":
    run()
