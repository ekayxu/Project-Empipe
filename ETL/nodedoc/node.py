#coding=utf-8
""""""
import re
from ordereddict import OrderedDict
from nodehandler import NodeHandlers
from namespace import Namespace as Space

class NodeBuilder(object):
	"""分解文档，返回节点对象列表
	"""
	Node_Delimiter = r'^##([\w.]+)##\s*$'
	Node_Locator = '.'

	def __init__(self, node_delimiter = ''):
		self.Node_Delimiter = node_delimiter or self.Node_Delimiter

	def __call__(self, source, handlers):
		if not hasattr(source, "readlines"):
			source = open(source, "rb")
		
		#节点前缀（父节点）决定该节点的处理方式
		getparent = lambda name: name.split(self.Node_Locator, 1)[0]
		return [Node(name, body, handlers.get(getparent(name))) for name, body in self._searchallnodes(source)]

	def _searchallnodes(self, source):
		delimiter = re.compile(self.Node_Delimiter)

		body = ''
		nodes = []
		lastnode = '#head'
		for line in source.readlines():
			line = unicode(line)
			nodedel = delimiter.findall(line)
			if nodedel:
				# print "node %s found!" % nodedel[0]
				nodes.append((lastnode.lower(), body))
				body = ''
				lastnode = nodedel[0]
			else:
				body += line
		nodes.append((lastnode.lower(), body))
		
		return nodes

class Node(object):
	"""
	节点类
	name
		节点名称
	text
		节点文本
	value
		节点值，渲染过后的结果，对
			上下文节点 返回 名字空间对象
			模板节点 返回渲染后的 文本
			文本节点 返回相同的文本
	handler
		节点处理静态类引用
	globalspace
		所属节点文档的全局空间
	"""
	def __init__(self, name, text, handler = None):
		self.name = name
		self.text = text
		self.globalspace = None
		self.sethandler(handler)
		self.value = None

	def sethandler(self, handler):
		self.handler = handler if handler else NodeHandlers.Default

	def activate(self):
		self.value = self.handler.make(self)
		return self.value
	
	@property
	def is_template(self):
		return issubclass(self.handler, NodeHandlers.Template)
	
	@property
	def is_context(self):
		return issubclass(self.handler, NodeHandlers.Context)

	def __repr__(self):
		return "Node object <%s: %s>" % (self.name, self.handler.__desc__)



class NodeCollection(object):
	"""
	节点集合/文档
		添加节点
		初始化context节点
		节点集合合并
		template节点渲染
		生成namespace对象
	"""

	_parser = NodeBuilder()
	handlers = {}

	def __init__(self, nodelist = [], init_space = {}):
		self.node = {} #OrderedDict()
		self.nodelist = OrderedDict()
		self.space = Space(init_space)

		for node in nodelist:
			node.globalspace = self.space
			self.nodelist[node.name] = node

	@classmethod
	def parse(cls, source):
		nodelist = cls._parser(source, cls.handlers)
		return cls(nodelist)
	
	@property
	def contexts(self):
		return [node for node in self if node.is_context]
	
	@property
	def templates(self):
		return [node for node in self if node.is_template]

	def fromspace(self, outspace):
		self.space += outspace
	
	def init_context(self, outspace):
		self.fromspace(outspace)

		for node in self.contexts:
			node.globalspace = self.space
			self.node[node.name] = Space(node.activate())
			self.space += self.node[node.name]
	
	init = init_context

	def render(self):
		for node in self.templates:
			node.globalspace = self.space
			node.activate()


	def __ilshift__(self, out_collection):
		out_collection.init(self.space)
		# self.space <<= out_collection.init(self.space)

		nodelist = self.nodelist
		for node in out_collection:
			name = node.name
			if name not in nodelist or not nodelist[name].text.strip():
				self.nodelist[name] = node
			else:
				if node.is_context and nodelist[name].is_context:
					nodelist[name].value <<= node.value
					self.space += nodelist[name].value
		
		return self
	
	def __iter__(self):
		return self.nodelist.itervalues()
	
	def tospace(self):
		return Space((node.name, node.value) for node in self)
	
def NodeDoc(name, handlers):
	return type(name, (NodeCollection,), dict(handlers = handlers))

if __name__ == '__main__':
	def test_nodecollection():
		pass
	
	test_nodecollection()

	def usecase_nc():
		# TaskML = makeCheeML('TaskML', NodeType_Mapping)
		TaskConf = NodeDoc('TaskConf', {})
		
	usecase_nc()