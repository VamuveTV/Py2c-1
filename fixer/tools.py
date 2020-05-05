from lib2to3.pygram import python_symbols as syms
from lib2to3.pytree import Leaf, Node

#从括号中取得信息并以list形式返回
def get_atom(node):
	item_list = []
	if node.type!=syms.atom:
		item_list.append(node.clone())
	elif node.children[1].type == syms.testlist_gexp:
		for i in range(len(node.children[1].children)):
			if i*2>=len(node.children[1].children):
				break
			elif(node.children[1].children[i*2].type==syms.atom):
				item_list+=get_atom(node.children[1].children[i*2])
			else:
				item_list.append(node.children[1].children[i*2].clone())
	else:
		item_list.append(node.children[1].clone())
	return item_list

#生成cin		
def deal_cin(node):
	return Node(syms.simple_stmt,[\
		Node(syms.power, [
			Leaf(1, 'std'),
			Node(syms.trailer, [
				Leaf(23, ':'),
				Leaf(23, ':'),
				Leaf(1, 'cin'),
			]),
		]),
		Leaf(34, '>>'),
		node.clone(),
		Leaf(1, ';'),
		Leaf(4, '\r\n'),])

#生成cout
def deal_cout(node):
	return Node(syms.simple_stmt,[\
		Node(syms.power, [
			Leaf(1, 'std'),
			Node(syms.trailer, [
				Leaf(23, ':'),
				Leaf(23, ':'),
				Leaf(1, 'cout'),
			]),
		]),
		Leaf(34, '<<'),
		node.clone(),
		Leaf(1, ';'),
		Leaf(4, '\r\n'),])

#文件头添加include
def add_include(node, file_name):
	#文件头注释
	temp = False
	if (node.children[0].type==syms.simple_stmt) \
		and (node.children[0].children[0].type==3):
		temp = node.children[0].clone()
		node.children[0].remove()
	#insert	
	insert_node = Leaf(1,'<'+file_name+'>')
	insert_node.prefix = ' '
	insert_node = Node(syms.import_name, [\
        Leaf(1, '#include'),\
		insert_node,\
        Leaf(4, '\r\n')])
	node.insert_child(0,insert_node)
	#node.children[0].prefix = node.children[1].prefix
	#node.children[1].prefix = ""
	if temp:
		node.insert_child(0,temp)

def add_lambda_define(node,args):
	#文件头注释
	temp = False
	from lib2to3.fixer_util import find_root
	overall = find_root(node)
	if (overall.children[0].type==syms.simple_stmt) \
		and (overall.children[0].children[0].type==3):
		temp = overall.children[0].clone()
		if overall.children[0].parent:
			overall.children[0].remove()
		else:
			del overall.children[0]
	#insert
	id = 0
	while overall.children[id].type == syms.lambdef:
		id+=1
	result = Node(syms.lambdef,[
		Leaf(1,'TODO_PyObject'),
		Leaf(1,'lambda_'+str(id),prefix=' '),
		]+args+[Leaf(4, '\r\n')])
	overall.insert_child(id,result)
	if temp:
		overall.insert_child(0,temp)
	return 'lambda_'+str(id)


############################
#		detect 相关
############################
	
#输入str，返回str对应缩进
def calculate_indent(node):
	indent = len(node)-1
	result = ""
	if indent <0:
		return result
	while (node[indent]=='\t')|(node[indent]==' '):
		result+= node[indent]
		indent-=1
		if indent<0:
			break
	return result

#更改str的缩进量,最好只对上一个结果使用	
#向下溢出让它报错
def change_indent(node,change_value):
	if len(node)!=0:
		if node[0]=='\t':
			return '\t'*(len(node)+change_value)
		else:
			return ' '*4*int((len(node)/4+change_value))
	else:
		return '\t'*change_value
			
#控制台以制表符形式的缩进
def new_line(indent):
	return '\t'*indent

from lib2to3.pytree import type_repr
#递归形式输出树
def recur(context,indent):
	result = new_line(indent)
	result += "%s(%s, "% (context.__class__.__name__, type_repr(context.type))
	#result += "%s, "% (context.prefix)
	if (len(context.children)==0):
		result += '\''
		if context.value =='\n':
			result+= "\\n\'"
		elif context.value =='\r\n':
			result+= "\\r\\n\'"
		else: 
			result += context.value + '\''
	else:
		result += "[\n"
		for i in context.children:
			result += recur(i,indent+1)
		result+=new_line(indent)+"]"
	result+="),\n"
	return result