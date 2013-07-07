# -*- coding: utf-8 -*-
from graph import Graph as WF
from lxml import etree
import gzip

def load(dia_file):
    doc = etree.parse(gzip.open(dia_file, 'rb'))
    root = doc.getroot()
    nsmap = root.nsmap
    nodes = root.xpath('//dia:object[@type="UML - State"]', namespaces=nsmap)
    archs = root.xpath('//dia:object[@type="Standard - Arc"]', namespaces=nsmap)
    id_names = {}
    wf = WF()
    # Build nodes
    for node in nodes:
        elems = node.xpath(
            'dia:attribute[@name="text"]/dia:composite/dia:attribute/dia:string',
            namespaces=nsmap)
        heads = node.xpath(
            'dia:attribute[@name="do_action"]/dia:string',
            namespaces=nsmap)
        if len(elems):
            elem = elems[0]
            name = elem.text.replace('#', '')
            id_names[node.attrib['id']] = name
            head = False
            if len(heads) and heads[0].text == '#HEAD#':
                head=True
            wf.add_node(name, head=head)
    # Build archs
    for arch in archs:
        connections = arch.xpath(
            'dia:connections/dia:connection', namespaces=nsmap)
        if len(connections) > 1:
            conn_from = id_names.get(connections[0].attrib['to'], False)
            conn_to = id_names.get(connections[1].attrib['to'], False)
            if (not conn_from) or (not conn_to):
                continue
            wf.add_arch(conn_from, conn_to)
    return wf

