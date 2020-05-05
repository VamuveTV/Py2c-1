#  Author: Xu Jing 

"""
	try 语句
"""

# 必需
from lib2to3 import fixer_base
from lib2to3.pytree import Leaf, Node
from lib2to3.pygram import python_symbols as syms
from lib2to3.pgen2 import token

class FixTry(fixer_base.BaseFix):

	BM_compatible = False	
	
	explicit = False		
	
	run_order = 6			

	PATTERN = """
		try_stmt<any*>
	"""

	def transform(self, node, results):
		args = []
		as_list = [[],[]]
		for i in node.children:
			if i.type == 11:
				args.append(Leaf(token.LBRACE, '{'))
			elif i.type == syms.suite:
				#as 语句
				for j in range(len(as_list[0])):
					args.append(i.children[0].clone())
					args.append(i.children[1].clone())
					args.append(Node(syms.simple_stmt,[\
						Leaf(1, 'auto'),
						as_list[0][j].clone(),
						Leaf(22, '='),
						as_list[1][j].clone(),
						Leaf(1, ';'),]))
				as_list[0] =[]
				as_list[1] =[]
				args.append(i.clone())
				args.append(Leaf(token.RBRACE, '}'))
				args.append(Leaf(4, '\r\n'))
				args.append(i.children[-1].clone())
			elif i.type == syms.except_clause:
				except_args = [Leaf(1, 'catch'),\
					Leaf(7, '(')]
				for j in i.children[1:]:
					#as 语句
					if (j.type==1)&(j.value=='as'):
						as_list[0].append(except_args[-1].clone())
					elif len(as_list[0])!=len(as_list[1]):
						as_list[1].append(j.clone())
						
					else:
						except_args.append(j.clone())
				except_args.append(Leaf(8, ')'))
				args.append(Node(syms.except_clause,except_args,prefix=i.prefix))
			else:
				args.append(i.clone())
		new = Node(node.type,args)
		new.prefix = node.prefix 
		return new