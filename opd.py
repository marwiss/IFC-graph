
from typing import Set, Dict, Optional, Any
from uuid import uuid4


class Node:
    id: int | str | None
    uuid: str | None
    label: str
    labels: Optional[Set[str]] = set()
    properties: Optional[Dict[str, Any]] = dict()

    def __init__(self, new_node_id: int,
                 new_node_label: str,
                 new_node_other_labels=None,
                 new_node_properties=None):
        if isinstance(new_node_id, int) and new_node_id > 0:
            self.id = new_node_id
            self.uuid = None
        else:
            uuid = str(uuid4())
            self.id = uuid
            self.uuid = uuid
        self.label = new_node_label
        self.properties = dict()
        self.properties.clear()
        self.labels = set()
        self.labels.clear()
        self.labels.add(new_node_label)
        self.labels.update(new_node_other_labels)
        self.properties['__instance_of'] = new_node_label
        self.properties['__step_file_id'] = self.id
        self.properties['__step_file_uuid'] = self.uuid
        for key, value in new_node_properties.items():
            self.properties[key] = value
        # print('Created instance of ' + new_node_label + ' __step_file_id ' + str(new_node_id))


# Create the basic node with literal attributes and the class hierarchy
def create_node(ifc_entity, ifc_file, hierarchy=False):

    # Set id and name of new node
    if ifc_entity.id() != 0:
        entity_id = ifc_entity.id()
    else:
        entity_id = None

    class_name = ifc_entity.is_a()

    # Add labels
    super_classes = list()
    super_classes.clear()
    # This alternative adds all super classes as labels - preserves IFC hierarchy
    if hierarchy:
        # Add all super classes of node class as labels
        for super_class in ifc_file.wrapped_data.types_with_super():
            if ifc_entity.is_a(super_class):
                super_classes.append(super_class)

    # Add properties
    property_types = ['ENTITY INSTANCE',
                      'AGGREGATE OF ENTITY INSTANCE',
                      'DERIVED']
    entity_properties = dict()
    entity_properties.clear()
    for i in range(ifc_entity.__len__()):
        if not ifc_entity.wrapped_data.get_argument_type(i) in property_types:
            key = ifc_entity.wrapped_data.get_argument_name(i)
            value = ifc_entity.wrapped_data.get_argument(i)
            entity_properties[key] = value

    # Create node object
    return Node(entity_id,
                class_name,
                super_classes,
                entity_properties)


def insert_node(node, session):

    cypher = """
        CALL apoc.create.node($labels, $properties);
    """

    result = session.run(cypher,
                         labels=list(node.labels),
                         properties=node.properties)


def insert_relationship(node, relationship, sub_node, session):

    cypher = """
        MATCH (from) WHERE from.__step_file_id = $from_id
        MATCH (to) where to.__step_file_id = $to_id
        CALL apoc.create.relationship(from, $type, $properties, to)
        YIELD rel
        RETURN count(rel)
    """

    result = session.run(cypher,
                         from_id=node.id,
                         to_id=sub_node.id,
                         type=relationship,
                         properties={})


# Process literal attributes, entity attributes, and relationship attributes
def create_nodes(session, ifc_entity, ifc_file):

    # Create and insert node
    node = create_node(ifc_entity, ifc_file)
    insert_node(node, session)

    # Create relationships to nodes without id
    for i in range(ifc_entity.__len__()):
        if ifc_entity[i]:
            if ifc_entity.wrapped_data.get_argument_type(i) == 'ENTITY INSTANCE':
                sub_node = create_node(ifc_entity[i], ifc_file)
                # Insert nodes part of entity declaration, without STEP id number, with created UUID
                if sub_node.uuid:
                    insert_node(sub_node, session)
                    # And create a relationship to the directly
                    insert_relationship(node, ifc_entity.wrapped_data.get_argument_name(i), sub_node, session)
    return


# Process literal attributes, entity attributes, and relationship attributes
def create_relationships(session, ifc_entity, ifc_file):

    # Create and insert node
    node = create_node(ifc_entity, ifc_file)

    # Create relationships from node
    for i in range(ifc_entity.__len__()):

        if ifc_entity[i]:

            if ifc_entity.wrapped_data.get_argument_type(i) == 'ENTITY INSTANCE':

                # Do not create relationship to IfcOwnerHistory
                # Do not create relationship from IfcProject
                if ifc_entity[i].is_a() in ['IfcOwnerHistory'] and ifc_entity.is_a() != 'IfcProject':
                    continue

                else:
                    sub_node = create_node(ifc_entity[i], ifc_file)
                    insert_relationship(node, ifc_entity.wrapped_data.get_argument_name(i), sub_node, session)

            elif ifc_entity.wrapped_data.get_argument_type(i) == 'AGGREGATE OF ENTITY INSTANCE':
                for sub_entity in ifc_entity[i]:
                    sub_node = create_node(sub_entity, ifc_file)
                    insert_relationship(node, ifc_entity.wrapped_data.get_argument_name(i), sub_node, session)

    # Create inverse relationships back to node
    for rel_name in ifc_entity.wrapped_data.get_inverse_attribute_names():
        if ifc_entity.wrapped_data.get_inverse(rel_name):
            inverse_relations = ifc_entity.wrapped_data.get_inverse(rel_name)
            for wrapped_rel_entity in inverse_relations:
                rel_entity = ifc_file.by_id(wrapped_rel_entity.id())
                sub_node = create_node(rel_entity, ifc_file)
                insert_relationship(node, rel_name, sub_node, session)
    return


def create_full_graph(graph_driver, ifc_file):
    idx = 1
    length = len(ifc_file.wrapped_data.entity_names())
    with graph_driver.session() as session:

        # Create nodes (and some relationships) first
        for entity_id in ifc_file.wrapped_data.entity_names():
            entity = ifc_file.by_id(entity_id)
            print(idx, '/', length, entity)
            create_nodes(session, entity, ifc_file)
            idx += 1

        # Then create relationships
        for entity_id in ifc_file.wrapped_data.entity_names():
            entity = ifc_file.by_id(entity_id)
            print(idx, '/', length, entity)
            create_relationships(session, entity, ifc_file)
            idx += 1
    return
