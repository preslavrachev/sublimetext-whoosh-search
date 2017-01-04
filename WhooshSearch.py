import sublime
import sublime_plugin
import fnmatch
import os
import sys

libs_dir = os.path.join(os.path.dirname(__file__), "libs")

# TODO:  Those are some dummy variables for test index creation within
# the plugin directory. Eventually, this data should come from the
# project properties
target_dir = os.path.dirname(__file__)
index_dir = os.path.join(target_dir, "index")
file_filter_pattern = "*.py"

if libs_dir not in sys.path:
	sys.path.append(libs_dir)

import whoosh
import whoosh.index as index
from whoosh.fields import Schema, TEXT

from whoosh.filedb.filestore import FileStorage

class IndexProject(sublime_plugin.TextCommand):
	def run(self, edit):
		# project_data = sublime.active_window().project_data()
		# project_dir = project_data['folders'][0]['path']

		# if the target directory does not exist, create it
		if not os.path.exists(index_dir):
			os.mkdir(index_dir)

		schema = Schema(path=TEXT, content=TEXT)
		ix = index.create_in(index_dir, schema)
		index_writer = ix.writer()

		for file_path in self.__list_files(file_filter_pattern):
			self.__add_doc(index_writer, file_path)

		index_writer.commit()

	def __list_files(self, file_filter_pattern):
		matched_files = []
		for root, dirnames, filenames in os.walk(target_dir):
			for filename in fnmatch.filter(filenames, file_filter_pattern):
				matched_files.append(os.path.join(root, filename))
		return matched_files

	def __add_doc(self, index_writer, file_path):
		file_object = open(file_path, "rb")
		content = file_object.read().decode("utf-8")
		file_object.close()
		index_writer.add_document(path=file_path, content=content)

class ClearIndex(sublime_plugin.TextCommand):
	def run(self, edit):
		index_exists = index.exists_in(target_dir)
