"""
	Author: XuJing
	基于2to3.refactor
"""

from __future__ import with_statement, print_function

import sys
import os
import logging
import shutil
import optparse
import io

from lib2to3.main import StdoutRefactoringTool
from lib2to3 import refactor
from lib2to3.pgen2 import driver, tokenize, token


#修改后缀名为cpp
def py_to_cpp(name):
	dot_position = name.rfind(os.extsep)
	return name[:dot_position]+os.extsep+"cpp"


class DIYRefactoringTool(StdoutRefactoringTool):
	"""
	A refactoring tool that can avoid overwriting its input files.
	Prints output to stdout.

	Output files can optionally be written to a different directory and or
	have an extra file suffix appended to their name for use in situations
	where you do not want to replace the input files.
	调用顺序 string -> feature -> tree
	"""

	def __init__(self, fixers, options, explicit, nobackups, show_diffs,
				 input_base_dir='', output_dir='', append_suffix=''):
		super(DIYRefactoringTool, self).__init__(fixers, options, explicit, nobackups, show_diffs, input_base_dir, output_dir, append_suffix)
	
	def refactor_tree(self, tree, name):
		"""Refactors a parse tree (modifying the tree in place).

		For compatible patterns the bottom matcher module is
		used. Otherwise the tree is traversed node-to-node for
		matches.

		Args:
			tree: a pytree.Node instance representing the root of the tree
				  to be refactored.
			name: a human-readable name for this tree.

		Returns:
			True if the tree was modified, False otherwise.
		"""
		#类型处理
		from fixer.pyobject_fix import recur_type
		recur_type(tree)
		#main处理
		from fixer.main_fix import fix_main
		if "main" not in tree.future_features:
			fix_main(tree)
		#print的import
		from fixer.tools import add_include
		if "print" in tree.future_features:
			add_include(tree,"iostream")
			add_include(tree,"stdio.h")
		#在2to3外运行该函数依赖
		from itertools import chain
		from lib2to3 import pytree, pygram
		from lib2to3.fixer_util import find_root
		
		for fixer in chain(self.pre_order, self.post_order):
			fixer.start_tree(tree, name)

		#use traditional matching for the incompatible fixers
		self.traverse_by(self.bmi_pre_order_heads, tree.pre_order())
		self.traverse_by(self.bmi_post_order_heads, tree.post_order())

		# obtain a set of candidate nodes
		match_set = self.BM.run(tree.leaves())

		while any(match_set.values()):
			for fixer in self.BM.fixers:
				if fixer in match_set and match_set[fixer]:
					#sort by depth; apply fixers from bottom(of the AST) to top
					match_set[fixer].sort(key=pytree.Base.depth, reverse=True)

					if fixer.keep_line_order:
						#some fixers(eg fix_imports) must be applied
						#with the original file's line order
						match_set[fixer].sort(key=pytree.Base.get_lineno)

					for node in list(match_set[fixer]):
						if node in match_set[fixer]:
							match_set[fixer].remove(node)

						try:
							find_root(node)
						except ValueError:
							# this node has been cut off from a
							# previous transformation ; skip
							continue

						if node.fixers_applied and fixer in node.fixers_applied:
							# do not apply the same fixer again
							continue

						results = fixer.match(node)

						if results:
							new = fixer.transform(node, results)
							if new is not None:
								node.replace(new)
								#new.fixers_applied.append(fixer)
								for node in new.post_order():
									# do not apply the fixer again to
									# this or any subnode
									if not node.fixers_applied:
										node.fixers_applied = []
									node.fixers_applied.append(fixer)

								# update the original match set for
								# the added code
								new_matches = self.BM.run(new.leaves())
								for fxr in new_matches:
									if not fxr in match_set:
										match_set[fxr]=[]

									match_set[fxr].extend(new_matches[fxr])

		for fixer in chain(self.pre_order, self.post_order):
			fixer.finish_tree(tree, name)
		#from fixer.tools import new_line,recur
		#test_me=recur(tree,0)
		#print (test_me)
		return tree.was_changed
		
	def refactor_string(self, data, name):
		try:
			tree = self.driver.parse_string(data)
		except Exception as err:
			self.log_error("Can't parse %s: %s: %s",
						   name, err.__class__.__name__, err)
			return
		finally:
			self.driver.grammar = self.grammar
		
		tree.future_features = self._detect_DIY_features(data)	#重要！通过对future_features中添加元素来传递文件范围的特征
		self.log_debug("Refactoring %s", name)
		self.refactor_tree(tree, name)
		return tree
	
	#寻找main标志
	def _detect_DIY_features(self,source):
		have_docstring = False
		gen = tokenize.generate_tokens(io.StringIO(source).readline)
		def advance():
			tok = next(gen)
			return tok[0], tok[1]
		ignore = frozenset({token.NEWLINE, tokenize.NL, token.COMMENT})
		features = set()
		try:
			while True:
				tp, value = advance()
				if tp in ignore:
					continue
				#main
				elif tp == token.STRING:
					if value == "'__main__'":
						features.add("main")
				elif tp == token.NAME and value == "main":
					features.add("main")
				#print
				elif (tp == token.NAME)&("print" not in features):
					if (value == "print")|(value == "input")|(value == "raw_input"):
						features.add("print")
				else:
					continue
		except StopIteration:
			pass
		return frozenset(features)
	
	
	
	def write_file(self, new_text, filename, old_text, encoding=None):
		"""Writes a string to a file.

		It first shows a unified diff between the old text and the new text, and
		then rewrites the file; the latter is only done if the write option is
		set.
		修改后缀名为cpp
		"""
		from fixer.comment_fix import adjust_comment
		from fixer.multistr_fix import adjust_multistr
		new_text = adjust_comment(new_text)
		new_text = adjust_multistr(new_text)
		new_filename = py_to_cpp(filename)
		try:
			fp = io.open(new_filename, "w", encoding=encoding, newline='')
		except OSError as err:
			self.log_error("Can't create %s: %s", new_filename, err)
			return

		with fp:
			try:
				fp.write(new_text)
			except OSError as err:
				self.log_error("Can't write %s: %s", new_filename, err)
		self.log_debug("Wrote changes to %s", new_filename)
		self.wrote = True

	PS1 = ">>> "
	PS2 = "... "


def warn(msg):
	print("WARNING: %s" % (msg,), file=sys.stderr)


def main(fixer_pkg, args=None):
	"""Main program.

	Args:
		fixer_pkg: the name of a package where the fixers are located.
		args: optional; a list of command line arguments. If omitted,
			  sys.argv[1:] is used.

	Returns a suggested exit status (0, 1, 2).
	"""
	# Set up option parser
	parser = optparse.OptionParser(usage="2to3 [options] file|dir ...")
	parser.add_option("-d", "--doctests_only", action="store_true",
					  help="Fix up doctests only")
	parser.add_option("-f", "--fix", action="append", default=[],
					  help="Each FIX specifies a transformation; default: all")
	parser.add_option("-j", "--processes", action="store", default=1,
					  type="int", help="Run 2to3 concurrently")
	parser.add_option("-x", "--nofix", action="append", default=[],
					  help="Prevent a transformation from being run")
	parser.add_option("-l", "--list-fixes", action="store_true",
					  help="List available transformations")
	parser.add_option("-p", "--print-function", action="store_true",
					  help="Modify the grammar so that print() is a function")
	parser.add_option("-v", "--verbose", action="store_true",
					  help="More verbose logging")
	"""
	parser.add_option("--no-diffs", action="store_true",
					  help="Don't show diffs of the refactoring")
	"""
	parser.add_option("-w", "--write", action="store_true",
					  help="Write back modified files")
	parser.add_option("-n", "--nobackups", action="store_true", default=False,
					  help="Don't write backups for modified files")
	parser.add_option("-o", "--output-dir", action="store", type="str",
					  default="", help="Put output files in this directory "
					  "instead of overwriting the input files.	Requires -n.")
	parser.add_option("-W", "--write-unchanged-files", action="store_true",
					  help="Also write files even if no changes were required"
					  " (useful with --output-dir); implies -w.")
	parser.add_option("--add-suffix", action="store", type="str", default="",
					  help="Append this string to all output filenames."
					  " Requires -n if non-empty.  "
					  "ex: --add-suffix='3' will generate .py3 files.")

	# Parse command line arguments
	refactor_stdin = False
	flags = {}
	options, args = parser.parse_args(args)
	if options.write_unchanged_files:
		flags["write_unchanged_files"] = True
		if not options.write:
			warn("--write-unchanged-files/-W implies -w.")
		options.write = True
	# If we allowed these, the original files would be renamed to backup names
	# but not replaced.
	if options.output_dir and not options.nobackups:
		parser.error("Can't use --output-dir/-o without -n.")
	if options.add_suffix and not options.nobackups:
		parser.error("Can't use --add-suffix without -n.")

	if not options.write :#and options.no_diffs:
		warn("not writing files and not printing diffs; that's not very useful")
	if not options.write and options.nobackups:
		parser.error("Can't use -n without -w")	   
	if options.list_fixes:
		print("Available transformations for the -f/--fix option:")
		for fixname in refactor.get_all_fix_names(fixer_pkg):
			print(fixname)
		if not args:
			return 0
	if not args:
		print("At least one file or directory argument required.", file=sys.stderr)
		print("Use --help to show usage.", file=sys.stderr)
		return 2
	if "-" in args:
		refactor_stdin = True
		if options.write:
			print("Can't write to stdin.", file=sys.stderr)
			return 2
	if options.print_function:
		flags["print_function"] = True

	# Set up logging handler
	level = logging.DEBUG if options.verbose else logging.INFO
	logging.basicConfig(format='%(name)s: %(message)s', level=level)
	logger = logging.getLogger('lib2to3.main')

	# Initialize the refactoring tool
	avail_fixes = set(refactor.get_fixers_from_package(fixer_pkg))
	unwanted_fixes = set(fixer_pkg + ".fix_" + fix for fix in options.nofix)
	explicit = set()
	if options.fix:
		all_present = False
		for fix in options.fix:
			if fix == "all":
				all_present = True
			else:
				explicit.add(fixer_pkg + ".fix_" + fix)
		requested = avail_fixes.union(explicit) if all_present else explicit
	else:
		requested = avail_fixes.union(explicit)
	fixer_names = requested.difference(unwanted_fixes)
	input_base_dir = os.path.commonprefix(args)
	if (input_base_dir and not input_base_dir.endswith(os.sep)
		and not os.path.isdir(input_base_dir)):
		# One or more similar names were passed, their directory is the base.
		# os.path.commonprefix() is ignorant of path elements, this corrects
		# for that weird API.
		input_base_dir = os.path.dirname(input_base_dir)
	if options.output_dir:
		input_base_dir = input_base_dir.rstrip(os.sep)
		logger.info('Output in %r will mirror the input directory %r layout.',
					options.output_dir, input_base_dir)
	rt = DIYRefactoringTool(
			sorted(fixer_names), flags, sorted(explicit),
			options.nobackups, False,#not options.no_diffs,
			input_base_dir=input_base_dir,
			output_dir=options.output_dir,
			append_suffix=options.add_suffix)

	# Refactor all files and directories passed as arguments
	if not rt.errors:
		if refactor_stdin:
			rt.refactor_stdin()
		else:
			try:
				rt.refactor(args, options.write, options.doctests_only,
							options.processes)
			except refactor.MultiprocessingUnsupported:
				assert options.processes > 1
				print("Sorry, -j isn't supported on this platform.",
					  file=sys.stderr)
				return 1
		rt.summarize()

	# Return error status (0 if rt.errors is zero)
	return int(bool(rt.errors))


if __name__ == '__main__':
	sys.exit(main("fixer"))