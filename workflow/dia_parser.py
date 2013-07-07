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

    for node in nodes:
        elems = node.xpath('dia:attribute[@name="text"]/dia:composite/dia:attribute/dia:string', namespaces=nsmap)
        if len(elems):
            elem = elems[0]
            name = elem.text.replace('#', '')
            id_names[node.attrib['id']] = name
            wf.add_node(name)
    for arch in archs:
        connections = arch.xpath('dia:connections/dia:connection', namespaces=nsmap)
        if len(connections) > 1:
            conn_from = id_names[connections[0].attrib['to']]
            conn_to = id_names[connections[1].attrib['to']]
            wf.add_arch(conn_from, conn_to)
    return wf

