#  Author: Xu Jing 

"""
	lambda 修改
	lambda x,y: x+y => TODO_PyObject lambda_xx( TODO_PyObject x, TODO_PyObject y) {return x+y;} 
						......
						lambda_xx
"""

# 必需
from lib2to3 import fixer_base
from lib2to3.pytree import Leaf, Node
from lib2to3.pygram import python_symbols as syms
from lib2to3.pgen2 import token
from .tools import add_lambda_define

def get_var(node):
	result = []
	if len(node.children)<2:
		result.append(node.clone())
	elif node.type == syms.varargslist:
		for i in range(len(node.children)):
			if i%2==0:
				result.append(node.children[i].clone())
	else:
		print('warning: lambda fixer error')
	return result
		
		

class FixLambda(fixer_base.BaseFix):

	BM_compatible = False	
	
	explicit = False		
	
	run_order = 4	

	PATTERN = """
		lambdef<
			'lambda'
			any*
		>
	"""

	def transform(self, node, results):
		arg_list = get_var(node.children[1])
		args = [Leaf(7, '(')]
		for i in arg_list:
			args.append(Leaf(1,'TODO_PyObject'))
			args.append(i)
			args.append(Leaf(12, ','))
		args[-1] = Leaf(8, ')')
		args.append(Leaf(token.LBRACE, '{'))
		args.append(Leaf(1, 'return'))
		expr = node.children[3].clone()
		expr.prefix = ' '
		args.append(expr)
		args.append(Leaf(1, ';'))
		args.append(Leaf(token.RBRACE, '}'))
		name = add_lambda_define(node,args)
		while(len(node.children)!=0):
			node.children[0].remove()
		node.append_child(Leaf(1,name))