# -*- coding: utf-8 -*-

__all__ = ['Graph']

class GraphNode(object):

    def __init__(self, name, to_online=None, roles=None, **kwargs):
        self.name = name
        self.to_online = to_online
        if roles is None:
            roles = []
        self.roles = roles
        self.__in = {}
        self.__out = {}

    def __repr__(self):
        return repr(self.__dict__())

    def __dict__(self):
        ret = {
            'name': self.name,
            'to_online': self.to_online,
            'outcoming': [elem.name for elem in self.outcoming.itervalues()],
            'incoming': [elem.name for elem in self.incoming.itervalues()],
            'roles': self.roles
        }
        return ret

    def __getitem__(self, key):
        return self.outcoming[key]

    def get(self, key, default=None):
        return self.outcouming.get(key, default=default)

    def _add_incoming(self, node, _first=True):
        if not self.__in.get(node.name, False):
            self.__in[node.name] = node
            if _first:
                node._add_outcoming(self, _first=False)
            return node

    def _add_outcoming(self, node, _first=True):
        if not self.__out.get(node.name, False):
            self.__out[node.name] = node
            if _first:
                node._add_incoming(self, _first=False)
            return node

    def _del_incoming(self, node, _first=True):
        name = node.name
        try:
            node = self.__in.pop(name)
        except KeyError:
            return None
        if _first:
            node._del_outcoming(self.name, _first=False)
        return node

    def _del_outcoming(self, node, _first=True):
        name = node.name
        try:
            node = self.__out.pop(name)
        except KeyError:
            return None
        if _first:
            node._del_incoming(self.name, _first=False)
        return node

    @property
    def outcoming(self):
        return self.__out.copy()

    @property
    def incoming(self):
        return self.__in.copy()


class Graph(object):

    def __init__(self, *names, **kwargs):
        self.__nodes = {}
        self.__head = None
        for idx, name in enumerate(names):
            self.add_node(name, **kwargs)

    def __repr__(self):
        return repr(self.__dict__())

    def __dict__(self):
        ret = {}
        for key, val in self.__nodes.iteritems():
            ret[key] = val.__dict__()
        return ret

    def __getitem__(self, key):
        return self.__nodes[key]

    def get(self, key, default=None):
        return self.__nodes.get(key, default=default)

    @classmethod
    def parse(cls, wf_dict):
        # build nodes
        wf = cls()
        for idx, val in enumerate(wf_dict.values()):
            wf = wf.add_node(**val)
        # build archs
        for key, val in wf_dict.iteritems():
            for out_key in val['outcoming']:
                wf.add_arch(key, out_key)
        return wf

    def add_node(self, name, head=False, **kwargs):
        node = GraphNode(name, **kwargs)
        if self.__head is None:
            self.__head = node
        if head:
            self.__head = node
        self.__nodes[node.name] = node
        return self

    def add_nodes(self, *names):
        [self.add_node(name) for name in names]
        return self

    def del_node(self, name):
        if self.__head.name == name:
            raise RuntimeError("Can not remove head")
        node = self.__nodes.pop(name)
        for node_out in node.outcoming.values():
            node._del_outcoming(node_out)
        for node_in in node.incoming.values():
            node._del_incoming(node_in)
        return self

    def add_arch(self, name_out, name_in):
        node_out = self.__nodes[name_out]
        node_in = self.__nodes[name_in]
        node_out._add_outcoming(node_in)
        return self

    def add_archs(self, *archs):
        [self.add_arch(arch[0], arch[1]) for arch in archs]
        return self

    @property
    def head(self):
        return self.__head

    @head.setter
    def head(self, value):
        self.__head = self.__nodes[value]