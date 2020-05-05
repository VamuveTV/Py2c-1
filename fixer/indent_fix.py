#  Author: Xu Jing 

"""
	对缩进的修改
	未完成
"""
import io
from lib2to3.pgen2 import tokenize,token
start_list = ['{','[','(']
end_list = ['}',']',')']

def adjust_comment(text):
	indent = []
	result = ""
	index = 0
	bracket_stack = 0
	while(index < len(text)):
		result+=text[index]
		if(text[index] in start_list):
			bracket_stack+=1
		elif (text[index] in end_list):
			bracket_stack-=1
		elif (text[index] == '\n'):
			if(bracket_stack>0):
				indent.append(bracket_stack)
			
	index +=1
	return text