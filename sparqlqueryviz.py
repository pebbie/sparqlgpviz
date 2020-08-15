import sys
import os.path as path
from rdflib import Namespace, XSD, RDF, RDFS, OWL
from rdflib.term import Variable, URIRef, BNode, Literal
from rdflib.plugins.sparql.parser import parseQuery
from rdflib.plugins.sparql.parserutils import prettify_parsetree
from rdflib.plugins.sparql import prepareQuery
from rdflib.paths import Path
import pprint
import pygraphviz as pgv
import argparse

BLANKNODES = []


def get_values(alg, vals):
    for obj in alg:
        k = list(obj.keys())[0]
        v = obj[k]
        lname = str(k)
        if lname in vals:
            vals[lname].append(v)
        else:
            vals[lname] = [v]


def find_triples(alg, vals):
    # TODO: draw different subqueries separately
    #print(type(alg))
    result = []
    if isinstance(alg, list):
        akg = alg
    else:
        akg = [alg]

    for al in akg:
        # pprint.pprint(al)
        if hasattr(al, 'name'):
            #print(al.name)
            #pprint.pprint(al)
            pass
        ak = dict(al).keys()
        for key in ak:
            if key in ['PV', 'var', '_vars', 'datasetClause', 'expr', 'op', 'A', 'lazy', 'service_string']:
                continue
            elif key == 'res' and isinstance(al[key], list):
                # values()
                get_values(al[key], vals)
                continue
            elif key == 'value':
                #pprint.pprint(al)
                #print(al[key])
                for var in al['var']:
                    vals[str(var)] = []
                for value in al[key]:
                    if isinstance(value, list):
                        for var in al['var']:
                            tmpval = value.pop(0)
                            vals[str(var)].append(tmpval)
                    else:
                        vals[str(var)].append(value)
                continue
            elif key == 'term':
                #print(type(al), al.name)
                #print(al)
                continue
            elif key == 'triples':
                # yield alg.triples
                result += [al.triples]
                continue
            #print(f'opening {key}')
            result += find_triples(al[key], vals)
    return result


def get_prefix(NS, uri):
    for k, v in sorted(NS.items(), key=lambda x: len(x[1]), reverse=True):
        if uri.startswith(str(v)):
            return k
    return None


def get_local_name(NS, uri):
    pref = get_prefix(NS, uri)
    return pref+':'+str(uri).replace(NS[pref], '') if pref is not None else str(uri)


def get_label(NS, term):
    tname = str(term)
    if isinstance(term, Variable):
        tname = '?' + tname
    elif isinstance(term, URIRef):
        tname = get_local_name(NS, term)
    elif isinstance(term, BNode):
        if tname not in BLANKNODES:
            BLANKNODES.append(tname)
        tname = '_:bn' + str(BLANKNODES.index(tname)+1)
    elif isinstance(term, Path):
        # print(term.n3())
        if hasattr(term, 'arg'):
            aname = get_local_name(NS, str(term.arg))
            tname = tname.replace(str(term.arg), aname)
        elif hasattr(term, 'args'):
            for arg in term.args:
                tname = tname.replace(str(arg), get_local_name(NS, arg))
        elif hasattr(term, 'path'):
            aname = get_local_name(NS, str(term.path))
            tname = tname.replace(str(term.path), aname)
        tname = tname[5:-1]
    return tname


def set_node_attr(viz, term, termlabel):
    n = viz.get_node(termlabel)
    if isinstance(term, Variable):
        n.attr['style'] = 'dashed'
    elif isinstance(term, BNode):
        n.attr['style'] = 'dotted'
    elif isinstance(term, Literal):
        n.attr['shape'] = 'box'
    return n


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '-infile', help="text file containing SPARQL query (.rq)", required=True)
    parser.add_argument(
        '-outfile', help="image file containing the visualized BGP (.png)")
    parser.add_argument(
        '-dot', action='store_true',
        help="when set, additionally create the dot file")
    parser.add_argument(
        '-ns', nargs='*',
        help="namespace prefix definition in the format of <prefix>=<prefixURI> or a filename of a text file containing this format for each line",
        default=[])
    parser.add_argument(
        '-verbose', action='store_true',
        help="print out intemediate debug info")
    parser.add_argument(
        '-layout', help="layout prog to pass on graphviz",
        default='dot',
        choices=['dot', 'neato', 'circo', 'fdp', 'sfdp', 'twopi'])

    args = parser.parse_args()

    if not path.exists(args.infile):
        print(f"{args.infile} does not exists. exiting..")
        sys.exit(1)

    if args.outfile is None:
        base, ext = path.splitext(args.infile)
        args.outfile = base + '.png'

    print(f"opening {args.infile}...")
    with open(args.infile) as fq:
        q = fq.read()

    NS = {"rdf": str(RDF), "rdfs": str(
        RDFS), "owl": str(OWL), "xsd": str(XSD)}

    for nsdef in args.ns:
        if path.exists(nsdef):
            with open(nsdef) as fns:
                for line in fns:
                    if line.startswith('#'):
                        # ignore comment
                        continue
                    prefix, nsURI = tuple(line.strip().split('='))
                    if prefix not in NS:
                        NS[prefix] = nsURI
        else:
            prefix, nsURI = tuple(nsdef.strip().split('='))
            if prefix not in NS:
                NS[prefix] = nsURI

    pq = prepareQuery(
        q, initNs=NS)

    #pprint.pprint(pq.algebra)
    #print(prettify_parsetree(pq.algebra))

    for prefix, nsURI in [n for n in pq.prologue.namespace_manager.namespaces()]:
        if prefix not in NS:
            NS[prefix] = str(nsURI)

    if args.verbose:
        pprint.pprint(pq.algebra)

    G = pgv.AGraph(directed=True)
    G.node_attr.update(colorscheme='accent8')
    G.edge_attr.update(colorscheme='accent8')

    values = {}
    tris = find_triples(pq.algebra, values)
    #pprint.pprint(tris)
    #exit()
    if tris is not None:
        for gid, trisgrp in enumerate(tris):
            for s, p, o in trisgrp:
                if args.verbose:
                    print(repr(s), repr(p), repr(o))
                    if not isinstance(p, URIRef):
                        print(type(p))

                # get term labels
                sname = get_label(NS, s)
                pname = get_label(NS, p)
                oname = get_label(NS, o)

                # add triple
                G.add_edge(sname, oname)

                # customize edge attribute
                edge = G.get_edge(sname, oname)
                if 'color' not in dict(edge.attr).keys():
                    edge.attr['color'] = gid+1
                edge.attr['label'] = pname
                if isinstance(p, Variable):
                    edge.attr['style'] = 'dashed'

                # customize node attribute
                snode = set_node_attr(G, s, sname)
                onode = set_node_attr(G, o, oname)

                #print(sname, oname, gid+1)

                if 'color' not in dict(snode.attr).keys():
                    snode.attr['color'] = gid+1
                if 'color' not in dict(onode.attr):
                    onode.attr['color'] = gid+1

    if len(values.keys()) > 0:
        for var in values:
            lname = str(var)
            varname = '?' + lname
            for value in values[lname]:
                valname = get_label(NS, value)
                G.add_edge(valname, varname)
                edge = G.get_edge(valname, varname)
                node = G.get_node(valname)
                node.attr['shape'] = 'box'
                edge.attr['style'] = 'dashed'
                edge.attr['dir'] = 'none'

    G.layout(prog=args.layout)

    if args.dot:
        base, ext = path.splitext(args.outfile)
        dotfile = base + '.dot'
        G.write(dotfile)
        print(f"writing {dotfile}...")

    print(f"writing {args.outfile}...")
    G.draw(args.outfile)
