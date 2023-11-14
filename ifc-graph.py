
import argparse
import os
from dotenv import load_dotenv

from neo4j import GraphDatabase
from py2neo import Graph

import ifcopenshell

import p2n
import opd

load_dotenv()

# Press the green button in the gutter to run the script.
if __name__ == "__main__":
    USAGE = """
        Visualize IFC STEP file.
        Usage: python ifc-graph.py -f /path/filename -a all|zhu|wiss
        Example python ifc-graph.py -f ./test.ifc -a zhu
    """
    parser = argparse.ArgumentParser(description=USAGE)
    parser.add_argument('-f', '--file', type=str, help='Input IFC STEP file path and file name',
                        default='test.ifc')
    parser.add_argument('-a', '--algorithm', type=str,
                        help='Write "all" to test all algorithms. Write "zhu" or "wiss" to test other algorithms',
                        default='all')
    args = parser.parse_args()

    # Parse IFC STEP file using IfcOpenShell
    print("Use IfcOpenShell to parse IFC STEP file.")
    my_ifc_file = ifcopenshell.open(args.file)

    # Connect to Neo4j database for Zhu py2neo algorithm
    print("Connecting to neo4j_py2neo using py2neo...")
    print("NEO4J_PY2NEO_URI", os.getenv('NEO4J_PY2NEO_URI'))
    print("NEO4J_USER", os.getenv('NEO4J_USER'))
    print("NEO4J_INITIAL_PASSWORD", os.getenv('NEO4J_INITIAL_PASSWORD'))
    try:
        py2neo_graph = Graph(os.getenv('NEO4J_PY2NEO_URI'),
                             auth=(os.getenv('NEO4J_USER'),
                                   os.getenv('NEO4J_INITIAL_PASSWORD')))
        py2neo_graph.run("MATCH (n) DETACH DELETE n")
        py2neo_graph.run("MATCH () RETURN 1 LIMIT 1")
        print('Connected.')
    except Exception:
        print('Could not establish connection.')

    # Connect to Neo4j database for Wiss official driver algorithm
    print("Connecting to neo4j_official using official driver...")
    print("NEO4J_OFFICIAL_URI", os.getenv('NEO4J_OFFICIAL_URI'))
    print("NEO4J_USER", os.getenv('NEO4J_USER'))
    print("NEO4J_INITIAL_PASSWORD", os.getenv('NEO4J_INITIAL_PASSWORD'))
    try:
        official_graph_driver = GraphDatabase.driver(os.getenv('NEO4J_OFFICIAL_URI'),
                                                     auth=(os.getenv('NEO4J_USER'),
                                                           os.getenv('NEO4J_INITIAL_PASSWORD')))
        official_graph_driver.verify_connectivity()
        official_graph_driver.execute_query("MATCH (n) DETACH DELETE n")
        official_graph_driver.execute_query("MATCH () RETURN 1 LIMIT 1")
        print('Connected.')
    except Exception:
        print('Could not establish connection.')

    # Insert using Zhu py2neo algorithm
    if args.algorithm in ('all', 'zhu'):
        p2n.create_full_graph(py2neo_graph, my_ifc_file)

    # Insert using Wiss official driver algorithm
    if args.algorithm in ('all', 'wiss'):
        opd.create_full_graph(official_graph_driver, my_ifc_file)
