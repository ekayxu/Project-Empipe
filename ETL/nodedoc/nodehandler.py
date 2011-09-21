#coding=utf-8
"""
标准节点处理器
"""
from Cheetah.Template import Template
from namespace import Namespace as Space
from errors import NodeError

class NodeHandler(object):
	"""节点处理器基类
	"""
	__desc__ = "Base"	
	@staticmethod
	def make(node):
		return node.text
	
class TextHandler(NodeHandler):
	__desc__ = "Text"
	pass

class ContextHandler(NodeHandler):
	__desc__ = "Context"

	@staticmethod
	def make(node):
		value = {}
		codetext = node.text.strip().replace('\r\n', '\n')
		#codetext = '#coding=utf-8\n' + node.text.strip().replace('\r\n', '\n')
		try:
			exec codetext in node.globalspace.__dict__.copy(), value
		except Exception, err:
			import traceback
			traceback.print_exc()
			raise NodeError, "Fail in Activating %s, err info: %s " % (node, err)
		
		return Space(value)

class TemplateHandler(NodeHandler):
	__desc__ = "Template"

	@staticmethod
	def make(node):
		try:
			return Template(node.text, node.globalspace).respond()
		except Exception, err:
			raise NodeError, "Fail in Rendering %s, err info: %s " % (node, err)

class NodeHandlers:
	Text = TextHandler
	Context = ContextHandler
	Template = TemplateHandler
	Default = TextHandler

if __name__ == '__main__':
	from node import Node
	from namespace import Namespace as Space
	def test_contextnode():
		text = "print 'test_contextnode'\na = 114\nb = {}\n"
		node = Node('test', text, NodeHandlers.Context)
		node.globalspace = Space()
		print node.activate()
		print node.globalspace
	test_contextnode()

	def test_templatenode():
		text = "HELLO, $name"
		node = Node('test', text, NodeHandlers.Template)
		node.globalspace = Space(dict(name = 'EK'))
		print node.activate()
		print node.globalspace
	test_templatenode()

	def test_emptytemplate():
		text = " "
		node = Node('test', text, NodeHandlers.Template)
		node.globalspace = Space(dict(name = 'EK'))
		print repr(node.activate())
		print node.globalspace
	test_emptytemplate()