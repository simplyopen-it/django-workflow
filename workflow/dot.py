# -*- coding: utf-8 -*-
import pydot

def plot(workflow, out_file):
    graph = pydot.Dot(graph_type='digraph')
    graph_nodes = {}
    for node in workflow.nodes.all():
        graph_nodes[node.name] = pydot.Node(node.label)
        graph.add_node(graph_nodes[node.name])
    for node_in, node_out in workflow.iterarchs():
        graph.add_edge(pydot.Edge(graph_nodes[node_in], graph_nodes[node_out]))
    graph.write_png(out_file)
