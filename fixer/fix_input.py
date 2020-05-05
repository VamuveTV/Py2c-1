#  Author: Xu Jing 

"""
	input 修改
	a = input("XXX") => cout<<"XXX"; cin>>a;
	auto a = input("XXX") => TODO_PyObject a; 
		cout<<"XXX";  cin>>a;
	raw_input 同理
"""

# 必需
from lib2to3 import fixer_base
from lib2to3.pytree import Leaf, Node
from lib2to3.pygram import python_symbols as syms
from lib2to3.pgen2 import token
from .tools import deal_cin,deal_cout

class FixInput(fixer_base.BaseFix):

	BM_compatible = False	
	
	explicit = False		
	
	run_order = 4			

	PATTERN = """
		simple_stmt<
			first = 'auto'*
			expr_stmt<
				name = any
				'='
				power<
					'input'
					out = any*
				>
			> 
			any*
		>
		|
		simple_stmt<
			first = 'auto'*
			expr_stmt<
				name = any
				'='
				power<
					'raw_input'
					out = any*
				>
			> 
			any*
		>
	"""

	def transform(self, node, results):
		args = []
		if results['first']:
			args.append(Node(syms.simple_stmt,[\
				Leaf(1, 'TODO_PyObject'),
				results['name'].clone(),
				Leaf(1, ';'),
				Leaf(4, '\r\n'),]))
		if results['out'][0].type==syms.trailer:
			args.append(deal_cout(results['out'][0].children[1]))
		args.append(deal_cin(results['name']))
		result = Node(syms.testlist1,args)
		result.prefix = node.prefix
		return result