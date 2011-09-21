#coding=utf-8
class Namespace:
	"""名字空间类
	
	集合运算:
		lspace + rpsace : 加法, 覆盖式更新
			将rspace中的变量添加至lspace中, 覆盖lspace中的变量
			等同于字典update操作, 即lspace.update(rspace)
		
		lspace << rspace : 左位移, 非覆盖更新. 
		    将rspace中的变量添加至lspace中, 但不覆盖lspace中的变量
		    类似但不等于 rspace + lspace
		    对所有的 v in lspace and v in rspace, 如果v也是容器类对象(dict或Namespace), 返回 lspace.v + rspace.v
	
	标准容器运算:
		设a是字符串, S 是Namespace对象

		a in S	:	如果S中存在名为a的对象则返回 True, 否则返回 False
		if S	:	若space非则空返回 True, 否则返回 False
		len(S)	:	返回S中变量个数
	
	约定:
		建议不使用类似 __xxx__ 的变量名
		如果非得有, 变量名不能是以下方法中的任何一个:
		__init__, __nonzero__, __len__, __contains__, __lshift__, __ilshift__, __add__, __iadd__, __iter__, __repr__
	"""

	def __init__(self, attrs = {}):
		self.__dict__ = dict(attrs)

	def __nonzero__(self):
		return len(self.__dict__)
	def __len__(self):
		return len(self.__dict__)
	def __contains__(self, attr):
		return attr in self.__dict__

	def __lshift__(lspace, rspace):
		left = lspace.__dict__.copy()
		right = rspace if isinstance(rspace, dict) else rspace.__dict__
		for k, v in right.iteritems():
			if k not in left:
				left[k] = v
			elif isinstance(left[k], (dict, Namespace)):
				if isinstance(v, dict):
					_v = v.copy()
					_v.update(left[k])
					left[k] = _v
				elif isinstance(v, Namespace):
					_v = Namespace(v)
					_v.__dict__.update(left[k])
					left[k] = _v

		return lspace.__class__(left)
	
	def __ilshift__(self, space):
		left = self.__dict__
		right = space if isinstance(space, dict) else space.__dict__
		for k, v in right.iteritems():
			if k not in left:
				left[k] = v
			elif isinstance(left[k], (dict, Namespace)):
				if isinstance(v, dict):
					_v = v.copy()
					_v.update(left[k])
					left[k] = _v
				elif isinstance(v, Namespace):
					_v = Namespace(v)
					_v.__dict__.update(left[k])
					left[k] = _v
		return self

	def __add__(lspace, rspace):
		left = lspace.__dict__.copy()
		right = rspace if isinstance(rspace, dict) else rspace.__dict__
		left.update(right)
		return lspace.__class__(left)

	def __iadd__(self, space):
		right = space if isinstance(space, dict) else space.__dict__
		self.__dict__.update(right)
		return self

	# def update(self, vars, **argpair):
	# 	self.__dict__.update(dict(vars))

	# def copy(self):
	# 	return self.__class__(self.__dict__.copy())
	def __setitem__(self, key, value):
		self.__dict__.__setitem__(key, value)
	
	def __getitem__(self, key):
		return self.__dict__.__getitem__(key)

	def __missing__(self):
		print "missing"
	def __iter__(self):
		return self.__dict__.iteritems()

	def __repr__(self):
		return repr(self.__dict__)


# from ordereddict import OrderedDict

# class OrderedSpace(Namespace):
# 	def __init__(self, attrs = {}):
# 		self.__dict__ = OrderedDict(attrs)

if __name__ == '__main__':
	from tita import timing

	def test_namespace():
		v = {'a': 114, 'b': {'abc': 77}}
		vi = {'abc': 114, 'ddd': {'abc': 77}}
		v1 = {'a': 114, 'b': Namespace(vi)}
		v2 = {'c': 69, 'b': {'abc': 123, 'ef': 81}}
		space = Namespace(v1)
		space2 = Namespace(v2)
		spacei = Namespace(vi)

		print "Namespace(space)",space
		print "Namespace(space2)", Namespace(space2)
		print "space | space2", space << space2

		space.i = 5
		print space, len(space)
		print  1 if Namespace() or not space else 0
		with timing("namespace or"):
			for i in xrange(100000):
				space << spacei
		with timing("namespace add"):
			for i in xrange(100000):
				space2 += space
		with timing("namespace new"):
			for i in xrange(100000):
				# Namespace(space2)
				space2 + space
				# space.__dict__.update(space2)
				# space.__dict__.update(space2.__dict__)

		del space.i
		class A(object):
			aa = 1
		a = A(); a.a = 'aaa'; a.ns = Namespace(v)
		print "space | a", space << a
		space3 =  Namespace(space)
		space3 += a
		print "space + a", space3
		space3['a'] = 908
		print space3['a']
	test_namespace()

	def test_with_ordereddict():
		from ordereddict import OrderedDict
		od = OrderedDict([('a', 1), ('b', 2), ('c', 3)])
		s = Namespace()
		s.__dict__ = od
		s += {'abc': 114, 'D': {'ABC': 77}}
		# print s.__dict__
		s.A = 1
		print s
	# test_with_ordereddict()