#  Author: Xu Jing 

"""
	for 循环
	只适用于c++11
"""

# 必需
from lib2to3 import fixer_base
from lib2to3.pytree import Leaf, Node
from lib2to3.pygram import python_symbols as syms
from lib2to3.pgen2 import token

class FixFor(fixer_base.BaseFix):

	BM_compatible = False	
	
	explicit = False		
	
	run_order = 6			

	PATTERN = """
		for_stmt< 
			'for'
			in_before=any* 
			'in' 
			in_after = any*
			'{'
			content = any* >
	"""

	def transform(self, node, results):
		args = [Leaf(1, 'for')]
		args += [Leaf(7, '(')]
		args += [Leaf(1, 'auto')]	 #c++11
		args += [n.clone() for n in results["in_before"]]
		args += [Leaf(token.COLON, ':')]
		args += [n.clone() for n in results["in_after"]]
		args += [Leaf(8, ')'),Leaf(token.LBRACE, '{')]
		args += [n.clone() for n in results["content"]]
		new = Node(node.type,args)
		new.prefix = node.prefix 
		return new