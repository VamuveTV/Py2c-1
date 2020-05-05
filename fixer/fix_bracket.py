#  Author: Xu Jing 

"""
	函数定义/for/while中增加花括号
	bug: 缩进——已解决
"""

# 必需
from lib2to3 import fixer_base
from lib2to3.pytree import Leaf, Node
from lib2to3.pygram import python_symbols as syms
from lib2to3.pgen2 import token
from .tools import calculate_indent
class FixBracket(fixer_base.BaseFix):

	BM_compatible = False	
	
	explicit = False		
	
	run_order = 5			


	PATTERN = """
		funcdef< head=any* colon=':' content=any* >
		|
		for_stmt< head=any* colon=':' content=any* >
		|
		while_stmt< head=any* colon=':' content=any* >
		|
		classdef< head=any* colon=':' content=any* >
	"""

	def transform(self, node, results):
		if(type(results["content"])==type(node)):
			args = [results["content"].clone()]
		else:	
			args = [n.clone() for n in results["content"]]
		for temp_leaf in args:
			if temp_leaf.type == syms.suite:
				indent_leaf = Leaf(token.RBRACE, '}')
				indent_leaf.prefix = calculate_indent(node.prefix)
				temp_leaf.insert_child(len(temp_leaf.children)-1,indent_leaf)
				temp_leaf.insert_child(len(temp_leaf.children)-1,Leaf(4, '\r\n'))
		args = [n.clone() for n in results["head"]] + [Leaf(token.LBRACE, '{')] + args
		new = Node(node.type,args)
		new.prefix = node.prefix 
		return new