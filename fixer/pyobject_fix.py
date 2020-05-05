#  Author: Xu Jing 

"""
	添加变量声明
	对外暴露recur_type
"""

from lib2to3.pytree import Leaf, Node
from lib2to3.pygram import python_symbols as syms

#判断是否为第一次出现，是的话修改node。
#返回bool型表示是否第一次出现
def judge_first(node,varlist,parent_node):
	if node.type!=1:
		return False
	if node.value not in varlist:
		parent_node.insert_child(0,Leaf(1, 'auto'))
		parent_node.children[0].prefix = parent_node.children[1].prefix
		parent_node.children[1].prefix = " "
		return True
	return False

#生成一个赋值语句节点(simple_stmt<expr_stmt<>>形式)
def form_eqs(node1,node2):
	result = Node(syms.simple_stmt,[\
		Node(syms.expr_stmt,[\
			node1.clone(),\
			Leaf(22, '='),\
			node2.clone()]),\
		Leaf(4, '\r\n')\
		])
	result.changed()
	return result

#上一个函数的mid形式，处理连等问题(a=b=XXX)
def form_mideqs(node1,node2_list):
	if len(node2_list)==1:
		result = node2_list[0].clone()
	else:
		args = []
		for i in node2_list:
			args.append(i.clone())
			args.append(Leaf(12, ','))
		args.pop()
		result = Node(syms.atom, [\
            Leaf(7, '('),\
            Node(syms.testlist_gexp, args),\
            Leaf(8, ')')])
	result = Node(syms.simple_stmt,[\
		Node(syms.expr_stmt,[\
			node1.clone(),\
			Leaf(22, '='),\
			result]),\
		Leaf(4, '\r\n')\
		])
	result.changed()
	return result

#处理等于号，理清逻辑
#不管类型问题
#结果没有clone
def eqs_deal(node):
	reorganized = {\
		'start' : [],\
		'mid' : [],\
		'end' : []
	}
	#逗号问题
	if node.children[0].type == syms.testlist_star_expr:
		for i in node.children[0].children:
			#非冒号直接插
			if(i.type!=12):
				reorganized['start'].append(i)
	else:
		reorganized['start'].append(node.children[0])
	#查中间
	for i in node.children[2:-2]:
		if(i.type!=22):
			reorganized['mid'].append(i)
	#查最后
	if node.children[-1].type == syms.testlist_star_expr:
		for i in node.children[-1].children:
			#非冒号直接插
			if(i.type!=12):
				reorganized['end'].append(i)
	else:
		reorganized['end'].append(node.children[-1])
	return reorganized



#变量声明
#WIT：作用域，类型，是否第一次,逗号问题
#每次递归对应node一层
#varlist结构为[[],[],[],...],每个小列表为一层作用域，模拟栈
#varlist里存储value而非节点
def recur_type(node,varlist=[[]]):
	#寻找函数参数并添加进varlist
	def function_recur(node,varlist):
		for i in node.children:
			if i.type==syms.parameters:
					for j in i.children:
						if j.type==syms.typedargslist:
							for k in j.children:
								if(k.type==1):
									varlist[-1].append(k.value)
						elif j.type==1:
							varlist[-1].append(j.value)
			recur_type(i,varlist)
			
	if(len(node.children)==0):
		return node
	for i in node.children:
		#递归
		if(i.type!=syms.expr_stmt):
			if(i.type==syms.funcdef):
				function_recur(i,varlist+[[]])
			elif(i.type==syms.classdef):
				recur_type(i,varlist+[[]])
			elif i.was_changed:
				continue	#是下级递归添加的
			elif i.type==syms.global_stmt:
				for j in i.children[1:]:
					if(j.type==1):
						varlist[-1].append(j.value)
			else:
				recur_type(i,varlist)
		#处理+=问题
		elif Leaf(22, '=') not in i.children:
			continue
		#处理赋值语句
		else:
			eqs_dict = eqs_deal(i)
			#不相等意味着存在多返回值函数
			if len(eqs_dict['start'])!=len(eqs_dict['end']):
				i.prefix+=" warning: multiple return value include "
				continue
			#start end处理 
			#TODO：prefix 测试
			parent_id = i.parent.parent.children.index(i.parent)
			for id in range(len(eqs_dict['start'])):
				node_now = form_eqs(eqs_dict['start'][id],eqs_dict['end'][id])
				if judge_first(eqs_dict['start'][id],varlist[-1],node_now):
					varlist[-1].append(eqs_dict['start'][id].value)
				if(id==0):
					node_now.prefix = i.prefix
					node_now.children[0].prefix = i.children[0].prefix
				i.parent.parent.insert_child(parent_id+id,node_now)
			parent_id+=len(eqs_dict['start'])
			#mid处理
			for id in range(len(eqs_dict['mid'])):
				node_now = form_mideqs(eqs_dict['mid'][id],eqs_dict['end'])
				if judge_first(eqs_dict['mid'][id],varlist[-1],node_now):
					varlist[-1].append(eqs_dict['mid'][id].value)
				i.parent.parent.insert_child(parent_id+id,node_now)
			i.parent.remove()		
		
