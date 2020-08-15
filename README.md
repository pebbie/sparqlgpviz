# SPARQL Graph Pattern visualization

Visualize Graph Pattern of a SPARQL Query

## Installation

requires `rdflib` and `pygraphviz` (depends on graphviz)

## Getting started

This program runs as command-line script. You need to save your query into a text file (e.g. `query.rq`).

`python3 sparqlgraphviz.py -i query.rq`

if the prefix declaration is not available in the query and you want to display compact URI for the node/edge label then you need to supply the namespace prefixes manually using the `-ns` parameter using `prefix=fullURI` format.

`python3 sparqlgraphviz.py -i query.rq -ns ch=http://purl.obolibrary.org/obo/`

or you can put all the prefixes in a text file. each line should be in the same format as in the `-ns` parameter above

for more examples, please look at `test.sh`