#  Author: Xu Jing 

"""
	功能：注释掉 global
"""

from lib2to3 import fixer_base
from lib2to3.pytree import Leaf, Node
from lib2to3.pygram import python_symbols as syms
from lib2to3.fixer_util import find_root

class FixGlobal(fixer_base.BaseFix):

	BM_compatible = False	
	
	explicit = False		
	
	run_order = 7		


	PATTERN = """
		global_stmt< any* >
	"""

	def transform(self, node, results):
		if 'main' in find_root(node).future_features:
			node.insert_child(0,Leaf(1, '#')) 
		return node