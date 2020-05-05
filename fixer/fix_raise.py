#  Author: Xu Jing 

"""
	功能：raise 改 throw
"""

from lib2to3 import fixer_base
from lib2to3.pytree import Leaf, Node
from lib2to3.pygram import python_symbols as syms
from lib2to3.fixer_util import find_root

class FixRaise(fixer_base.BaseFix):

	BM_compatible = False	
	
	explicit = False		
	
	run_order = 5		


	PATTERN = """
		raise_stmt< any* >
	"""

	def transform(self, node, results):
		node.children[0].value = 'throw'