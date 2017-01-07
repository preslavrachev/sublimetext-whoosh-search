import sublime
import sublime_plugin
import fnmatch
from functools import reduce
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
from whoosh.fields import Schema, TEXT, STORED
from whoosh.qparser import QueryParser

from whoosh.filedb.filestore import FileStorage


class BaseCommand():
	def foo(self):
		return "bar"

	def get_file_content(self, file_path, mode="rb"):
		file_object = open(file_path, "rb")
		content = file_object.read().decode("utf-8")
		file_object.close()

		return content


class IndexProject(sublime_plugin.TextCommand, BaseCommand):
	def run(self, edit):
		# project_data = sublime.active_window().project_data()
		# project_dir = project_data['folders'][0]['path']

		# if the target directory does not exist, create it
		if not os.path.exists(index_dir):
			os.mkdir(index_dir)

		schema = Schema(path=STORED, content=TEXT)
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
		content = self.__get_file_content(file_path)

		index_writer.add_document(path=file_path, content=content)


class SearchProject(sublime_plugin.WindowCommand, BaseCommand):
	def run(self):
		self.window.show_input_panel("Enter search query:", "", self.__execute_do_search, None, None)

	def __execute_do_search(self, query):
		rsl = self.__get_search_results(query)
		self.window.show_quick_panel(rsl, lambda: self.window.active_view().hide_popup(), 0, 0, lambda idx: self.window.active_view().show_popup(str(rsl[idx][1])))

	def __get_search_results(self, query):	
		ix = index.open_dir(index_dir)

		qp = QueryParser("content", schema=ix.schema)
		q = qp.parse(query)

		results = []
		with ix.searcher() as searcher:
			hits = searcher.search(q, limit=None)

			for hit in hits:
				result = [hit["path"]]
				
				content = BaseCommand.get_file_content(self, hit["path"])
				highlights = hit.highlights("content", text=content)
				hl_string = reduce(lambda hl1, hl2: "" + hl1 + "..." + hl2, highlights, "")

				result.append(highlights)
				results.append(result)	

		return results


class ClearIndex(sublime_plugin.TextCommand):
	def run(self, edit):
		index_exists = index.exists_in(target_dir)
