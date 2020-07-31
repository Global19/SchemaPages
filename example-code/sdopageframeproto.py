#!/usr/bin/env python2.7
import sys
import os
sys.path.append( os.getcwd() )
sys.path.insert( 1, 'markdown' ) #Pickup libs, rdflib etc., from shipped lib directory
import rdflib
from sdotermsource import *
from sdoterm import *
from localmarkdown import Markdown

Markdown.setWikilinkCssClass("localLink")
Markdown.setWikilinkPrePath("/")


triplesfile = "data/schemaorg-all-https.nt"
termgraph = rdflib.Graph()
termgraph.parse(triplesfile, format="nt")

print ("loaded %s triples" % len(termgraph))

SdoTermSource.setQueryGraph(termgraph)
terms = terms = SdoTermSource.getAllTerms()
print ("Terms Count: %s" % len(terms))

import schemapages_pb2

sdotypemap = {
    SdoTerm.TYPE: schemapages_pb2.TermType.TYPE,
    SdoTerm.PROPERTY: schemapages_pb2.TermType.PROPERTY,
    SdoTerm.DATATYPE: schemapages_pb2.TermType.DATATYPE,
    SdoTerm.ENUMERATION: schemapages_pb2.TermType.ENUMERATION,
    SdoTerm.ENUMERATIONVALUE: schemapages_pb2.TermType.ENUMERATIONVALUE,
    SdoTerm.REFERENCE: schemapages_pb2.TermType.REFERENCE
}

def term2protomsg(termid):
    term = SdoTermSource.getTerm(termid)
    if term.termType == SdoTerm.TYPE or term.termType == SdoTerm.DATATYPE or term.termType == SdoTerm.ENUMERATION:
        msg = schemapages_pb2.SDOBaseType()
    elif term.termType == SdoTerm.PROPERTY:
        msg = schemapages_pb2.SDOProperty()
    elif term.termType == SdoTerm.ENUMERATIONVALUE:
        msg = schemapages_pb2.SDOEnumerationValue()
    elif term.termType == SdoTerm.REFERENCE:
        msg = schemapages_pb2.SDOReference()
    else:
        print("Unknown term type '%s'" % term.termType)


    msg.id = term.id

    msgterm = msg.termdescriptor.add()

    msgterm.termType = sdotypemap[term.termType]
    msgterm.uri = term.uri
    msgterm.label = term.label
    msgterm.acknowledgements.extend(term.acknowledgements)
    for i in term.superPaths:
        sp = msgterm.superPaths.add()
        sp.superPath.extend(i)
    msgterm.comment = term.comment
    msgterm.equivalents.extend(term.equivalents)
    msgterm.pending = term.pending
    msgterm.retired = term.retired
    msgterm.sources.extend(term.sources)
    msgterm.subs.extend(term.subs)
    msgterm.supers.extend(term.supers)


    if term.termType == SdoTerm.TYPE or term.termType == SdoTerm.DATATYPE or term.termType == SdoTerm.ENUMERATION:
        msg.properties.extend(term.properties)
        msg.expectedTypeFor.extend(term.expectedTypeFor)
        if term.termType == SdoTerm.ENUMERATION:
            msg.enumerationMembers.extend(term.enumerationMembers)
        msg.supersedes.extend(term.supersedes)
        msg.termStack.extend(term.termStack)
    elif term.termType == SdoTerm.PROPERTY:
        msg.domainIncludes.extend(term.domainIncludes)
        msg.rangeIncludes.extend(term.rangeIncludes)
        msg.supersedes.extend(term.supersedes)
        msg.termStack.extend(term.termStack)
    elif term.termType == SdoTerm.ENUMERATIONVALUE:
        msg.enumerationParent = term.enumerationParent
        msg.supersedes.extend(term.supersedes)
    elif term.termType == SdoTerm.REFERENCE:
        pass



    msgstr = msg.SerializeToString()
    return msgstr
    
#print(':'.join(x.encode('hex') for x in msgstr))
import time,datetime
start = datetime.datetime.now()
for t in terms:
    tic = datetime.datetime.now()
    ms = term2protomsg(t)
    filename = "protomsgs/" + t +".msg"
    f = open(filename,"w")
    f.write(ms)
    f.close()
    print("Term: %s - %s" % (t, str(datetime.datetime.now()-tic)))
print ("All terms took %s seconds" % str(datetime.datetime.now()-start))
    



