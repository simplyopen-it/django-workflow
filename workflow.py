class WorkflowNode(object):

    def __init__(self, name, start=False, end=False,
                 incoming=None, outcoming=None):
        self.name = name
        if incoming is None:
            incoming = {}
        if outcoming is None:
            outcoming = {}
        self.__in = incoming
        self.__out = outcoming

    def __repr__(self):
        return repr(self.__dict__())

    def __dict__(self):
        ret = {
            'name': self.name,
            'outcoming': self.outcoming,
        }
        return ret

    def __getitem__(self, key):
        return self.outcoming[key]

    def add_incoming(self, node, _first=True):
        if isinstance(node, (str, unicode)):
            node = WorkflowNode(node)
        if not self.__in.get(node.name, False):
            self.__in[node.name] = node
            if _first:
                node.add_outcoming(self, _first=False)
            return node

    def add_outcoming(self, node, _first=True):
        if isinstance(node, (str, unicode)):
            node = WorkflowNode(node)
        if not self.__out.get(node.name, False):
            self.__out[node.name] = node
            if _first:
                node.add_incoming(self, _first=False)
            return node

    def del_incoming(self, node, _first=True):
        name = node
        if isinstance(node, WorkflowNode):
            name = node.name
        try:
            node = self.__in.pop(name)
        except KeyError:
            return None
        if _first:
            node.del_outcoming(self.name, _first=False)
        return node

    def del_outcoming(self, node, _first=True):
        name = node
        if isinstance(node, WorkflowNode):
            name = node.name
        try:
            node = self.__out.pop(name)
        except KeyError:
            return None
        if _first:
            node.del_incoming(self.name, _first=False)
        return node

    @property
    def outcoming(self):
        return self.__out.copy()

    @property
    def incoming(self):
        return self.__in.copy()


class Workflow(object):

    def __init__(self, *stat_names):
        self._stats = {}
        for stat_name in stat_names:
            self._stats[stat_name] = WorkflowNode(stat_name)

    def add_node(self, node):
        if isinstance(node, (str, unicode)):
            if self._stats.get(node, False):
                raise RuntimeError("Node with name '%s' already present." % node)
            self._stats[node] = WorkflowNode(node)
            return self._stats[node]
        elif isinstance(node, WorkflowNode):
            if self._stats.get(node.name, False):
                raise RuntimeError("Node with name '%s' already present." % node)
            self._stats[node.name] = node
            return node
        else:
            raise AttributeError("A string or WorkflowNode expected, %s received instead." % type(node))

