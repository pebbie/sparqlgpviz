#!/bin/bash

#clear

PR="" #"-l sfdp"
echo $PR

#rm *.png

python3 sparqlgraphviz.py -i simple/all.rq $PR
python3 sparqlgraphviz.py -i simple/allclasses.rq  $PR
python3 sparqlgraphviz.py -i rhea/q1.rq $PR 
python3 sparqlgraphviz.py -i rhea/q2.rq $PR 
python3 sparqlgraphviz.py -i rhea/q3.rq $PR
python3 sparqlgraphviz.py -i rhea/q4.rq $PR
python3 sparqlgraphviz.py -i rhea/q5.rq $PR
python3 sparqlgraphviz.py -i rhea/q6.rq $PR
python3 sparqlgraphviz.py -i rhea/q7.rq $PR
python3 sparqlgraphviz.py -i rhea/q8.rq $PR
python3 sparqlgraphviz.py -i rhea/q9.rq $PR
python3 sparqlgraphviz.py -i rhea/q10.rq $PR
python3 sparqlgraphviz.py -i rhea/q11.rq $PR
python3 sparqlgraphviz.py -i rhea/q12.rq $PR
python3 sparqlgraphviz.py -i wikidata/lastNitems.rq $PR -ns wikidata/wikidata.prefixes 
python3 sparqlgraphviz.py -i wikidata/lastNitems_nolbl.rq $PR -ns wikidata/wikidata.prefixes 
