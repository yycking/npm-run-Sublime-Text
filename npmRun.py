import sublime
import sublime_plugin

import os
import re
import subprocess
import shlex

class NpmRunListener(sublime_plugin.EventListener):
	def on_init(self,views):
		for view in views:
			self.prepare(view)
			
	def on_load(self, view):
		self.prepare(view)

	def on_modified(self, view):
		self.prepare(view)

	def prepare(self, view):
		file_path = view.file_name()
		file_name = os.path.basename(file_path)
		if file_name != 'package.json':
			return

		regex = '\"scripts\":\s*(\{\s*[^{]*?\})'
		area = view.find(regex, 0)
		substr = view.substr(area)
		scripts = re.search(regex, substr)
		start = area.begin() + scripts.start(1)
		regions = []
		command = []
		for script in re.finditer('\"([^:,\n]*?)\":', scripts[1]):
			key = script[1]
			command.append('npm run <a href="'+key+'">'+ key+'</a>')

			region = sublime.Region(start + script.start(1), start+ script.end(1))
			regions.append(region)

		def run(command):
			path = os.path.dirname(file_path)
			cmd = f"cd {path} && npm run {command} "
			subprocess.run(
				shlex.split(
					f"""osascript -e 'tell app "Terminal" to activate' -e 'tell app "Terminal" to do script "{cmd}" '"""
				)
			)

		view.erase_regions("npm script")
		view.add_regions("npm script", regions, "", '', sublime.HIDDEN | sublime.PERSISTENT, command, 'Crimson', run)
