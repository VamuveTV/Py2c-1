#  Author: Xu Jing 

"""
	功能：加分号
	多行注释转换为单行注释
"""

# 必需
from lib2to3 import fixer_base
from lib2to3.pytree import Leaf, Node
from lib2to3.pygram import python_symbols as syms
from lib2to3.pgen2 import token

#	命名必须和文件名相匹配，比如fix_XXX.py就对应这里的FIXXXX
#	但是不同的是，XXX的首字母这里必须大写。
#	需要继承fixer_base.BaseFix
class FixSemicolon(fixer_base.BaseFix):

	BM_compatible = False	
	
	explicit = False		
	
	run_order = 5		


	PATTERN = """
		simple_stmt< any* >
	"""

	def transform(self, node, results):
		#将多行注释转化为单行注释
		if (node.children[0].type==3):
			node.children[0].value = node.children[0].value.replace('\"\"\"','#',1)
			node.children[0].value = node.children[0].value.replace('\"\"\"','',1)
			node.children[0].value = node.children[0].value.replace('\n','\n#')
			return node.clone()
		#其他
		node.insert_child(len(node.children)-1,Leaf(1, ';')) 
		return node.clone()