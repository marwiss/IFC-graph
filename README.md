# IFC-graph
Import IFC data from STEP file into Neo4j LPG

## Background

This algorithm is based on original work described in the paper:

* IFC-graph for facilitating building information access and query
* By Junxiang Zhu, Peng Wu, Xiang Lei
* In the journal "Automation in construction"

https://www.sciencedirect.com/science/article/pii/S0926580523000389

## What's new

However, in this repo the algorithm have been rewritten to use the
official python driver for neo4j instead of py2neo. Py2neo is discontinued.

https://community.neo4j.com/t/farewell-py2neo-what-happens-now/64419

The new algorithm is more procedural because py2neo is an OGM while the official driver is not.

I was thinking about making this code more object oriented in the future.

## Disclaimer

The new algorithm should be tested on larger IFC STEP-files to verify
that the produced graph is correct. This has not yet been done.

To make this algorithm more suitable for importing larger IFC STEP-files
it might be necessary to look at some batch import features or apoc.periodic.iterate.

This is an early version. There could be some errors and mistakes in the code.

A lot of improvements can be made to the code.
