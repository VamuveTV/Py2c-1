#  Author: Xu Jing 

"""
	对注释格式的修改
"""
import io
from lib2to3.pgen2 import tokenize,token

def adjust_comment(text):
	gen = tokenize.generate_tokens(io.StringIO(text).readline)
	result = []
	try:
		while True:
			tok = next(gen)
			if(tok[0]==token.COMMENT)\
			and not tok[1].startswith('#include')\
			and not tok[1].startswith('#define'):
				result.append((tok[0],\
				tok[1].replace('#','//',1),\
				tok[2],tok[3],tok[4]))
			else:
				result.append(tok)
	except StopIteration:
		pass
	return tokenize.untokenize(result[:-1])
