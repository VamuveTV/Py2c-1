# XuJing 

"""
	Fixer for detect Node Structure.
"""
from lib2to3 import fixer_base
from lib2to3.pytree import type_repr
from .tools import new_line,recur
	

class FixDetect(fixer_base.BaseFix):
	BM_compatible = True
	
	explicit = True
	
	PATTERN = """
		file_input<parens=any*>
	"""
	
	def transform(self, node, results):
		result = ""
		if type(results['parens'])!=type([]):
			result=recur(results['parens'],0)
		else:
			for i in results['parens']:
				result+=recur(i,0)
		print(result)
		#print(results['parens'])