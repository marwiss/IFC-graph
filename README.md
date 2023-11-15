# IFC-graph
Import IFC data from STEP file into Neo4j LPG

This algorithm is based on original work described in the paper:

* IFC-graph for facilitating building information access and query
* By Junxiang Zhu, Peng Wu, Xiang Lei
* In the journal "Automation in construction"

https://www.sciencedirect.com/science/article/pii/S0926580523000389

However, in this repo the algorithm have been rewritten to use the
official python driver for neo4j instead of py2neo. Py2neo is discontinued.

https://community.neo4j.com/t/farewell-py2neo-what-happens-now/64419

The new algorithm is quite different because py2neo is an OGM while the official driver is not.

