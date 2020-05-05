#  Author: Xu Jing 

"""
	print 修改
	print a,b => std.cout<<a<<b
	print "%s",%d => printf("%s",d)
"""

# 必需
from lib2to3 import fixer_base
from lib2to3.pytree import Leaf, Node
from lib2to3.pygram import python_symbols as syms
from lib2to3.pgen2 import token
from .tools import deal_cout,get_atom

class FixPrint(fixer_base.BaseFix):

	BM_compatible = False	
	
	explicit = False		
	
	run_order = 4			

	PATTERN = """
		simple_stmt<print_stmt<any*> any*>
	"""

	def transform(self, node, results):
		#处理"%s" %d问题
		def deal_term(node):
			from lib2to3.fixer_util import Call
			args = []
			args+=get_atom(node.children[0])
			for i in range(1,len(node.children)):
				if i%2==1:
					continue
				args+=get_atom(node.children[i])
			temp = len(args)-1
			for i in range(temp):
				args.insert(2*i+1,Leaf(12, ','))
			return Node(syms.simple_stmt,[\
				Call(Leaf(1,'printf'),args),
				Leaf(1, ';'),
				Leaf(4, '\r\n'),])
		
		item_list = []
		i=1
		args = []
		while i<len(node.children[0].children):
			item_list.append(node.children[0].children[i])
			i+=2
		for item in item_list:
			if item.type==syms.atom:
				item_list.insert(item_list.index(item)+1,item.children[1])
			elif item.type==syms.testlist_gexp:
				i=0
				while i<len(item.parent.children)/2:
					item_list.insert(item_list.index(item)+i+1,item.children[i*2])
					i+=1
			elif item.type==syms.term:
				args.append(deal_term(item))
			else:
				args.append(deal_cout(item))
		result = Node(syms.testlist1,args)
		result.prefix = node.prefix
		return result