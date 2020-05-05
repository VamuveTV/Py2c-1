#  Author: Xu Jing 

"""
	assert 修改
	assert x,y,z => if (!((x)&&(y)&&(z)))
					{throw "AssertionError";}
"""

# 必需
from lib2to3 import fixer_base
from lib2to3.pytree import Leaf, Node
from lib2to3.pygram import python_symbols as syms
from lib2to3.pgen2 import token

class FixAssert(fixer_base.BaseFix):

	BM_compatible = False	
	
	explicit = False		
	
	run_order = 4			

	PATTERN = """
		simple_stmt<
			assert_stmt<any*>
			any*
		>
	"""

	def transform(self, node, results):
		args = []
		for i in range(len(node.children[0].children)):
			if i%2==1:
				if i!=1:
					args.append(Leaf(1, '&&'))
				args.append(Leaf(7, '('))
				args.append(node.children[0].children[i].clone())
				args.append(Leaf(8, ')'))
		args = [\
			Leaf(1, 'if'),Leaf(7, '('),\
			Leaf(1, '!'),Leaf(7, '('),\
			Node(syms.and_expr,args),\
			Leaf(8, ')'),Leaf(8, ')'),\
			Leaf(token.LBRACE, '{'),\
			Node(syms.raise_stmt, [
                        Leaf(1, 'throw'),
                        Leaf(3, '"AssertionError"'),
						Leaf(1, ';'),
                ]),
			Leaf(token.RBRACE, '}'),Leaf(4, '\r\n')
		]
		
		result = Node(syms.testlist1,args)
		result.prefix = node.prefix
		return result