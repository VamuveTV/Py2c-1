#  Author: Xu Jing 

"""
	对注释格式的修改
"""
import io
from lib2to3.pgen2 import tokenize,token

def adjust_multistr(text):
	gen = tokenize.generate_tokens(io.StringIO(text).readline)
	result = []
	try:
		while True:
			tok = next(gen)
			if(tok[0]==token.STRING)and \
			tok[1].startswith('"""'):
				result_str = tok[1].replace('"""','"')
				result_str = result_str.replace('\r\n','\\n')
				result_str = result_str.replace('\n','\\n')
				result.append((tok[0],\
				result_str,\
				tok[2],tok[3],tok[4]))
			else:
				result.append(tok)
	except StopIteration:
		pass
	return tokenize.untokenize(result[:-1])