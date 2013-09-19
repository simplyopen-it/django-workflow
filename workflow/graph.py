# -*- coding: utf-8 -*-
# pylint: disable=E0202

__all__ = ['Graph']


class _GraphNode(object):
    ''' Reppresentation of an oriented-graph node.

    Each graph node must have a unique name in the graph where it
    belongs.

    You are free to add whatever other attribute you need by passing
    them as keyword arguments.

    Graph nodes are linked together with lists of incoming and
    outcoming nodes. You can add/remove nodes by calling the
    appropriete methods:

    add_incoming(node)
    add_outcoming(node)
    del_incoming(node)
    del_outcoming(node)

    All This methods must be feeded with a _GraphNode instance which
    is then returned; adding or removing a _GraphNode instance modify
    the current instance and the one involved.

    You can access lists of incoming and outcoming nodes as normal
    dictionaries, but those returned by properties 'outcoming' and
    'incoming' are shallow copies of internal dictionaries.

    A _GraphNode is represented as a dictionary on print.
    '''

    def __init__(self, name, label=None, online=None, roles=None, **kwargs):
        '''
        '''
        self.name = name
        if label is None:
            label = name
        self.label = label
        self.online = online
        if roles is None:
            roles = []
        self.roles = roles
        self.__attrs = kwargs
        self.__in = {}
        self.__out = {}

    def __repr__(self):
        return repr(self.__dict__)

    @property
    def __dict__(self):
        ret = self.__attrs.copy()
        ret['name'] = self.name
        ret['label'] = self.label
        ret['online'] = self.online
        ret['roles'] = self.roles
        ret['outcoming'] = [elem.name for elem in self.outcoming.itervalues()]
        ret['incoming'] = [elem.name for elem in self.incoming.itervalues()]
        return ret

    def __getattr__(self, name):
        try:
            return self.__attrs['name']
        except KeyError:
            raise AttributeError("Object has no attribute '%s'" % name)

    @property
    def outcoming(self):
        return self.__out.copy()

    @property
    def incoming(self):
        return self.__in.copy()

    def add_incoming(self, node, _first=True):
        if not self.__in.get(node.name, False):
            self.__in[node.name] = node
            if _first:
                node.add_outcoming(self, _first=False)
            return node

    def add_outcoming(self, node, _first=True):
        if not self.__out.get(node.name, False):
            self.__out[node.name] = node
            if _first:
                node.add_incoming(self, _first=False)
            return node

    def del_incoming(self, node, _first=True):
        name = node.name
        try:
            node = self.__in.pop(name)
        except KeyError:
            return None
        if _first:
            node.del_outcoming(self, _first=False)
        return node

    def del_outcoming(self, node, _first=True):
        name = node.name
        try:
            node = self.__out.pop(name)
        except KeyError:
            return None
        if _first:
            node.del_incoming(self, _first=False)
        return node


class Graph(object):
    ''' An oriented graph.

    An oriented graph is a set of nodes with their respective incoming
    and outcoming lists.

    An oriented graph can be accessed like a normal python dictionary,
    but element(s) can be added or removed just by calling the
    appropriete methods:

    add_node()/add_nodes()
    del_node()/del_nodes()

    When a node is added it is created as an isoleted node, that means
    without any incoming or outcoming arch. To add or remove arch(s)
    use the appropriate methods:

    add_arch()/add_archs()
    del_arch()/del_archs()

    Every Graph method returns a reference to the Graph itself, this
    is to permit a dot notation sequence of Graph updates; example:

    >>> Graph().add_node('one').add_node('two').add_arch('one', 'two')
    or just
    >>> Graph().add_nodes('one', 'two').add_arch('one', 'two)
    Will produce a graph with to nodes linked with an arch.

    '''
    def __init__(self, *names, **kwargs):
        head = None
        if kwargs.has_key('head') and kwargs['head'] in names:
            head = kwargs.pop('head')
        self.__nodes = {'__HEAD__': head}
        for name in names:
            self.add_node(name, **kwargs)
        if self.__nodes['__HEAD__'] is not None:
            self.__head = self.__nodes[self.__nodes['__HEAD__']]

    @classmethod
    def parse(cls, wf_dict):
        # build nodes
        head = None
        if wf_dict.has_key('__HEAD__'):
            head = wf_dict.pop('__HEAD__')
        wf = cls()
        for val in wf_dict.values():
            wf = wf.add_node(**val)
        # build archs
        for key, val in wf_dict.iteritems():
            for out_key in val['outcoming']:
                wf.add_arch(key, out_key)
        if head is not None:
            wf.head = head
        return wf

    ################
    # Python magic #
    ################

    def __repr__(self):
        return repr(self.__dict__)

    @property
    def __dict__(self):
        ret = {}
        for key, val in self.__nodes.iteritems():
            try:
                ret[key] = val.__dict__
            except AttributeError:
                ret[key] = val
        return ret

    def __getitem__(self, key):
        return self.__nodes[key]

    ################################
    # Getters/Settes and iterators #
    ################################

    def bf_walk(self):
        ''' Perform a Breadtth-First-Walk on the graph (starting
        from head and return an ordered list.
        '''
        q = [self.head]
        marked = {self.head.name : True}
        ret = [self.head]
        while len(q) > 0:
            curr = q.pop()
            for elem in curr.outcoming.itervalues():
                if not marked.get(elem.name, False):
                    marked[elem.name] = True
                    q.insert(0, elem)
                    ret.append(elem)
        return ret

    def filter(self, **kwargs):
        ret = []
        for node in self.itervalues():
            ok = True
            for attr, value in kwargs.iteritems():
                if attr.endswith('__in'):
                    ok &= getattr(node, attr.strip('__in')) in value
                else:
                    ok &= getattr(node, attr) == value
            if ok:
                ret.append(node)
        return ret

    def get_nodes_by_roles(self, roles):
        if not hasattr(roles, '__iter__'):
            roles = [roles]
        return [
            node for name, node in self.__nodes.iteritems()
            if name != '__HEAD__' and \
            (len(node.roles) == 0 or \
             set(roles).intersection(node.roles))]

    def deepcopy(self):
        return self.__class__.parse(self.__dict__)

    def get(self, key, *args):
        return self.__nodes.get(key, *args)

    @property
    def head(self):
        return self.__head

    @head.setter
    def head(self, value):
        self.__head = self.__nodes[value]
        self.__nodes['__HEAD__'] = self.__head.name

    def keys(self):
        return [key for key in self.__nodes.keys() if key != '__HEAD__']

    def iterkeys(self):
        for key in self.__nodes.iterkeys():
            if key != '__HEAD__':
                yield key

    def values(self):
        return [val for key, val in self.__nodes.items() if key != '__HEAD__']

    def itervalues(self):
        for key, val in self.__nodes.iteritems():
            if key != '__HEAD__':
                yield val

    def items(self):
        return [(key, val) for key, val in self.__nodes.items() if key != '__HEAD__']

    def iteritems(self):
        for key, val in self.__nodes.iteritems():
            if key != '__HEAD__':
                yield (key, val)

    ##################################
    # Methods to modify the Workflow #
    ##################################

    def add_node(self, name, head=False, inplace=True, **kwargs):
        if not inplace:
            self = self.deepcopy()
        node = _GraphNode(name, **kwargs)
        self.__nodes[node.name] = node
        if head:
            self.__head = node
            self.__nodes['__HEAD__'] = node.name
        return self

    def add_nodes(self, *names, **kwargs):
        if not kwargs.get('inplace', True):
            self = self.deepcopy()
            kwargs.pop('inplace')
        for name in names:
            self.add_node(name, **kwargs)
        return self

    def del_node(self, name, inplace=True):
        if not inplace:
            self = self.deepcopy()
        if self.__head.name == name:
            raise RuntimeError("Can not remove head")
        node = self.__nodes.pop(name)
        for node_out in node.outcoming.values():
            node.del_outcoming(node_out)
        for node_in in node.incoming.values():
            node.del_incoming(node_in)
        return self

    def del_nodes(self, *names, **kwargs):
        if not kwargs.get('inplace', True):
            self = self.deepcopy()
            kwargs.pop('inplace')
        for name in names:
            self.del_node(name)
        return self

    def add_arch(self, name_out, name_in, inplace=True):
        if not inplace:
            self = self.deepcopy()
        node_out = self.__nodes[name_out]
        node_in = self.__nodes[name_in]
        node_out.add_outcoming(node_in)
        return self

    def add_archs(self, *archs, **kwargs):
        if not kwargs.get('inplace', True):
            self = self.deepcopy()
            kwargs.pop('inplace')
        for arch in archs:
            self.add_arch(arch[0], arch[1])
        return self

    def del_arch(self, name_out, name_in, inplace=True):
        if not inplace:
            self = self.deepcopy()
        node_out = self.__nodes[name_out]
        node_in = self.__nodes[name_in]
        node_out.del_outcoming(node_in)
        return self

    def del_archs(self, *archs, **kwargs):
        if not kwargs.get('inplace', True):
            self = self.deepcopy()
            kwargs.pop('inplace')
        for arch in archs:
            self.del_arch(arch[0], arch[1])
        return self
