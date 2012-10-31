import sublime, sublime_plugin, platform, subprocess

PLATFORM_IS_WINDOWS = platform.system() is 'Windows'


class StylusCompileCommand(sublime_plugin.TextCommand):
	
	PANEL_NAME = "styluscompile_output"
	DEFAULT_STYLUS_EXECUTABLE = 'stylus.cmd' if PLATFORM_IS_WINDOWS else 'stylus'
	SETTINGS = sublime.load_settings("StylusCompile.sublime-settings")


	def run(self, edit):
		text = self._get_text_to_compile()
		window = self.view.window()

		css, error = self._compile(text, window)
		self._write_output_to_panel(window, css, error)

			
	def _compile(self, text, window):	
		args = self._get_stylus_args()

		try:
			process = subprocess.Popen(args,
				stdin=subprocess.PIPE,
				stdout=subprocess.PIPE,
				stderr=subprocess.PIPE,
				startupinfo=self._get_startupinfo())
			return process.communicate(text)

		except OSError as e:
			error_message = 'StylusCompile error:'
			if e.errno is 2:
				error_message += 'No se encontro el ejecutable "stylus".'
			error_message += str(e)				

			sublime.status_message(error_message)
			return('', error_message)

	def _write_output_to_panel(self, window, css, error):
		panel = window.get_output_panel(self.PANEL_NAME)
		panel.set_syntax_file('Packages/CSS/CSS.tmLanguage')

		text = css or str(error)
		self._write_to_panel(panel, text)

		window.run_command('show_panel', {'panel': 'output.%s' % self.PANEL_NAME})

	def _write_to_panel(self, panel, text):
		panel.set_read_only(False)
		edit = panel.begin_edit()
		panel.insert(edit, 0, text)
		panel.end_edit(edit)
		panel.sel().clear()
		panel.set_read_only(True)

	def _get_text_to_compile(self):
		region = self._get_selected_region() if self._editor_contains_selected_text() \
			else self._get_region_for_entire_file()
		return self.view.substr(region)

	def _get_region_for_entire_file(self):
		return sublime.Region(0, self.view.size())

	def _get_selected_region(self):
		return self.view.sel()[0]

	def _editor_contains_selected_text(self):
		for region in self.view.sel():
			if not region.empty():
				return True
		return False

	def _get_stylus_args(self):
		stylus_executable = self._get_stylus_executable()
		command = "%s" % (stylus_executable)
		return command

	def _get_stylus_executable(self):
		return self.SETTINGS.get('stylus_executable') or self.DEFAULT_STYLUS_EXECUTABLE

	def _get_startupinfo(self):
		if PLATFORM_IS_WINDOWS:
			info = subprocess.STARTUPINFO()
			info.dwFlags |= subprocess.STARTF_USESHOWWINDOW
			info.wShowWindow = subprocess.SW_HIDE
			return info
		return None

