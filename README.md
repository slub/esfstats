# python-esfstats - elasticsearch fields statistics

python-esfstats is a Python3 program that extracts some statistics regarding field coverage from an elasticsearch index.

## Usage

```
python-esfstats
        -h, --help    show this help message and exit
        -host HOST    hostname or IP address of the elasticsearch instance to use, default is localhost.
        -port PORT    port of the elasticsearch instance to use, default is 9200.
        -index INDEX  elasticsearch index to use
        -type TYPE    elasticsearch index type to use
        -marc         ignore MARC indicator
```

* example:
    ```
    python-esfstats -host [HOSTNAME OF YOUR ELASTICSEARCH INSTANCE] -index [YOUR ELASTICSEARCH INDEX] -type [DOCUMENT TYPE OF THE ELEASTICSEARCH INDEX] > [OUTPUT STATISTICS DOCUMENT]
    ```

## Requirements

[elasticsearch-py](http://elasticsearch-py.rtfd.org/)

e.g.
```
apt-get install python-elasticsearch
```

## Run

* install elasticsearch-py
* clone this git repo or just download the python_esfstats.py file
* run ./python_esfstats.py
* for a hackish way to use python-esfstats system-wide, copy to /usr/local/bin

### Install system-wide via pip

* via pip:
    ```
    sudo -H pip3 install --upgrade [ABSOLUTE PATH TO YOUR LOCAL GIT REPOSITORY OF PYTHON-ESFSTATS]
    ```
    (which provides you ```python-esfstats``` as a system-wide commandline command)

## Description

(of the column headers of a resulting statistic)

### ... in English

#### existing
* number of records that contain this field (path), i.e., field coverage

#### %
* ^ percentage of 'existing'
* (existing / Total Records * 100)

#### notexisting
* number of records that do not contain this field (path)

#### !%
* ^ percentage of 'notexisting'
* (not existing / Total Records * 100)

#### occurrence
* total count of the occurrence of this field (path) over all records, i.e., an indicator for field where multiple values are allowed

#### unique (appr.)
* number of unique/distinct values of this field (path), i.e., cardinality
* note: this value is an approximated value

#### field name
* the field (path) of this statistic line

### ... in German

Erklärung der Spaltenköpfe

#### existing
* gibt an, wieviele Felder diesen Pfades existieren.

#### %
* existing in Prozent
* existing / Total Records * 100

#### notexisting
* gibt an, wieviele Rekords nicht über diesen Pfad verfügen

#### !%
* notexisting in Prozent
* notexisting / Total Records * 100)

#### occurrence
* gibt an, wieviele Werte diesen Pfades vorhanden sind. (Mehrfachbelegung)

#### unique (appr.)
* gibt an, wieviele einzigartige Werte man in diesem Pfad findet
* Hinweis: dieser Wert ist nur angenähert berechnet, d.h., er ist u.U. ungenau

#### field name
* Der Pfad zu den analysierten Werten


