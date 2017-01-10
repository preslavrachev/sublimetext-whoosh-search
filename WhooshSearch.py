import sublime
import sublime_plugin
import fnmatch
from functools import reduce
import os
import sys

libs_dir = os.path.join(os.path.dirname(__file__), "libs")

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

	def get_target_dir(self):
		window = self.window if hasattr(self, 'window') else self.view.window()
		folders = window.folders()
		return folders[0]

	def get_index_dir(self):
		print(self)
		return os.path.join(self.get_target_dir(), "index")


class IndexProject(sublime_plugin.TextCommand, BaseCommand):
	def run(self, edit):
		index_dir = BaseCommand.get_index_dir(self)
		target_dir = BaseCommand.get_target_dir(self)

		# if the target directory does not exist, create it
		if not os.path.exists(index_dir):
			os.mkdir(index_dir)

		schema = Schema(path=STORED, content=TEXT)
		ix = index.create_in(index_dir, schema)
		index_writer = ix.writer()

		for file_path in self.__list_files(target_dir, file_filter_pattern):
			self.__add_doc(index_writer, file_path)

		index_writer.commit()

	def __list_files(self, target_dir, file_filter_pattern):
		matched_files = []
		for root, dirnames, filenames in os.walk(target_dir):
			for filename in fnmatch.filter(filenames, file_filter_pattern):
				matched_files.append(os.path.join(root, filename))
		return matched_files

	def __add_doc(self, index_writer, file_path):
		content = BaseCommand.get_file_content(self, file_path)

		index_writer.add_document(path=file_path, content=content)


class SearchProject(sublime_plugin.WindowCommand, BaseCommand):
	def run(self):
		self.index_dir = BaseCommand.get_index_dir(self)
		self.window.show_input_panel("Enter search query:", "", self.__execute_do_search, None, None)

	def __execute_do_search(self, query):
		ix = index.open_dir(self.index_dir)
		rsl = self.__get_search_results(query, ix)
		self.window.show_quick_panel(rsl, lambda: self.window.active_view().hide_popup(), 0, 0, lambda idx: self.window.active_view().show_popup(str(rsl[idx][1])))

	def __get_search_results(self, query, ix):
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


class ClearIndex(sublime_plugin.WindowCommand):
	def run(self, edit):
		#index_exists = index.exists_in(target_dir)
		print("fuck")
		BaseCommand.get_index_dir(self)
