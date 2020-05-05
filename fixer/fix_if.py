#  Author: Xu Jing 

"""
	If 条件
	包括花括号和括号
	无缩进
"""

# 必需
from lib2to3 import fixer_base
from lib2to3.pytree import Leaf, Node
from lib2to3.pygram import python_symbols as syms
from lib2to3.pgen2 import token

class FixIf(fixer_base.BaseFix):
	BM_compatible = False	
	explicit = True	
	run_order = 6			

	PATTERN = """ 
			if_stmt< any* >
	"""

	def transform(self, node, results):
		args = []
		item_id = 0
		while item_id <len(node.children):
			if (node.children[item_id].__class__.__name__=="Leaf"):
				if node.children[item_id].value==':':
					#加花括号
					args+=[Leaf(token.LBRACE, '{'),
					node.children[item_id+1].clone(),
					Leaf(token.RBRACE, '}'),
					Leaf(4, '\r\n')
					]
					item_id+=1
				#if，elif处理
				elif (node.children[item_id].value=='elif') | (node.children[item_id].value=='if'):
					if node.children[item_id].value=='elif':
						leaf_temp = Leaf(1, 'if')
						leaf_temp.prefix = " "
						args+=[Leaf(1, 'else'),leaf_temp]
					else:
						args+=[node.children[item_id].clone()]
					args+=[Leaf(7, '(')]
					args+=[node.children[item_id+1].clone()]
					args+=[Leaf(8, ')')]
					item_id+=1
				else:
					args+=[node.children[item_id].clone()]
			else:
				print("\nFixerError_if\n")
			item_id+=1
		new = Node(node.type,args)
		new.prefix = node.prefix 
		return new