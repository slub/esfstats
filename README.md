# esfstats-python - elasticsearch fields statistics

esfstats-python is a Python program that extracts some statistics re. field coverage in the documents.

You need to install elasticsearch python lib.

## Usage

```
esfstats 
        -host   hostname or IP of the elasticsearch instance
        -port   port of the native Elasticsearch transport protocol API
        -index  index name
        -type   document type
        -help   print this help
	-marc	ignore Marc identifier field if you are analysing an index of marc records
```

