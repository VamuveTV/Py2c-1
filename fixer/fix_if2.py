#  Author: Xu Jing 

"""
	If 条件
	包括花括号和圆括号
	部分解决缩进问题
"""

# 必需
from lib2to3 import fixer_base
from lib2to3.pytree import Leaf, Node
from lib2to3.pygram import python_symbols as syms
from lib2to3.pgen2 import token
from .tools import calculate_indent
from .tools import change_indent

class FixIf2(fixer_base.BaseFix):
	BM_compatible = False	
	explicit = False
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
					#取：号下一行的第二个元素前的空行，因为第一个元素是换行。
					leaf_temp0 = Leaf(token.RBRACE, '}')
					leaf_temp0.prefix = change_indent(calculate_indent(node.children[item_id+1].children[1].value), -1)
					#加花括号
					args+=[Leaf(token.LBRACE, '{'),
					node.children[item_id+1].clone(),
					Leaf(4, '\r\n'),
					leaf_temp0,
					Leaf(4, '\r\n')]
					item_id+=1
				#if，elif处理
				elif (node.children[item_id].value=='elif') | (node.children[item_id].value=='if'):
					if node.children[item_id].value=='elif':
						leaf_temp0 = Leaf(1, 'else')
						leaf_temp0.prefix = change_indent(calculate_indent(node.children[item_id+3].children[1].value), -1)
						leaf_temp1 = Leaf(1, 'if')
						leaf_temp1.prefix = " "
						args+=[leaf_temp0,leaf_temp1]
					else:
						args+=[node.children[item_id].clone()]
					args+=[Leaf(7, '(')]
					args+=[node.children[item_id+1].clone()]
					args+=[Leaf(8, ')')]
					item_id+=1
				else:
					leaf_temp0 = node.children[item_id].clone()
					if(node.children[item_id].value=='else'):
						leaf_temp0.prefix = change_indent(calculate_indent(node.children[item_id+2].children[1].value), -1)
					args+=[leaf_temp0]
			else:
				print("\nFixerError_if\n")
			item_id+=1
		new = Node(node.type,args)
		new.prefix = node.prefix 
		return new