#  Author: Xu Jing 

"""
	类定义
"""

# 必需
from lib2to3 import fixer_base
from lib2to3.pytree import Leaf, Node
from lib2to3.pygram import python_symbols as syms
from lib2to3.pgen2 import token
from .tools import calculate_indent
class FixClass(fixer_base.BaseFix):

	BM_compatible = False	
	
	explicit = False		
	
	run_order = 6			


	PATTERN = """
		classdef< any*>
	"""

	def transform(self, node, results):
		args = []
		for i in range(len(node.children)):
			if len(node.children[i].children)!=0:
				args.append(node.children[i].clone())
			elif node.children[i].value=='{':
				args.append(Leaf(token.LBRACE, '{'))
				args.append(Leaf(4, '\r\n'))
				args.append(Leaf(1,'public'))
				args.append(Leaf(11,':'))
			elif node.children[i].value=='(':
				if node.children[i+1].type!=8:
					args.append(Leaf(11,':'))
			elif node.children[i].value==')':
				pass
			else:
				args.append(node.children[i].clone())
		result_node = Node(syms.classdef,args,prefix = node.prefix)
		return result_node