#  Author: Xu Jing 

"""
	添加main函数
"""
from lib2to3.pytree import Leaf, Node
from lib2to3.pygram import python_symbols as syms

#main函数
def fix_main(node):
	main_list = []
	del_list =[]
	
	if(len(node.children)==0):
		return node
	# 处理文件头多行注释
	temp = False
	if (node.children[0].type==syms.simple_stmt) \
		and (node.children[0].children[0].type==3):
		temp = node.children[0].clone()
		node.children[0].remove()
	
	for i in node.children:
		if(i.type==syms.funcdef)|(i.type==syms.async_funcdef)|(i.type==syms.classdef)|(i.type==syms.decorated):
			continue
		if len(i.children)!=0:
			if(i.children[0].type==syms.import_name)|(i.children[0].type==syms.import_from):
				continue
		main_list.append(i.clone())
		del_list.append(i)
	
	for i in del_list:
		i.remove()
	if temp:
		node.insert_child(0,temp)
	args = [
		Leaf(1, 'def'),
		Leaf(1, 'main',prefix=' '),
		Node(syms.parameters, [
				Leaf(7, '('),
				Leaf(8, ')'),
		]),
		Leaf(11, ':'),
		Leaf(4, '\r\n')
	]
	args+=main_list
	args+=[Node(syms.suite, [
				Leaf(5, '\t'),
				Node(syms.simple_stmt, [
						Node(syms.return_stmt, [
								Leaf(1, 'return '),
								Leaf(2, '0'),
						]),
						Leaf(4, '\r\n'),
				]),
				Leaf(6, '')
	])]
	main_node = Node(syms.funcdef,args)
	node.append_child(main_node)	
	