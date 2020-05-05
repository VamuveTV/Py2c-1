#  Author: Xu Jing 

"""
	函数定义
	TODO:为 main 添加return
"""

# 必需
from lib2to3 import fixer_base
from lib2to3.pytree import Leaf, Node
from lib2to3.pygram import python_symbols as syms
from lib2to3.pgen2 import token
from .tools import calculate_indent
class FixFunc(fixer_base.BaseFix):

	BM_compatible = False	
	
	explicit = False		
	
	run_order = 6			


	PATTERN = """
		funcdef<
			'def'
			name=any* 
			parameters< any* > 
			end = any* 
		>
	"""

	def transform(self, node, results):
		if node.children[1].value=='main':
			node.children[0].value = 'int'
		else:
			node.children[0].value = 'TODO_PyObject'
		for i in node.children:
			if i.type==syms.parameters:
				for j in i.children:
					if j.type==syms.typedargslist:
						for k in j.children:
							if(k.type==1):
								k.prefix+='TODO_PyObject '
					elif j.type==1:
						j.prefix+='TODO_PyObject '
		return node