#  Author: Xu Jing 

"""
	while 循环
"""

# 必需
from lib2to3 import fixer_base
from lib2to3.pytree import Leaf, Node
from lib2to3.pygram import python_symbols as syms
from lib2to3.pgen2 import token

class FixWhile(fixer_base.BaseFix):

	BM_compatible = False	
	
	explicit = False		
	
	run_order = 6			

	PATTERN = """
		while_stmt< 
			'while'
			test_content = any*
			'{'
			content = any* >
	"""

	def transform(self, node, results):
		args = [Leaf(1, 'while')]
		args += [Leaf(7, '(')]
		args += [n.clone() for n in results["test_content"]]
		args += [Leaf(8, ')'),Leaf(token.LBRACE, '{')]
		args += [n.clone() for n in results["content"]]
		new = Node(node.type,args)
		new.prefix = node.prefix 
		return new