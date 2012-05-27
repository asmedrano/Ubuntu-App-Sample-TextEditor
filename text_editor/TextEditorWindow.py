# -*- Mode: Python; coding: utf-8; indent-tabs-mode: nil; tab-width: 4 -*-
### BEGIN LICENSE
# This file is in the public domain
### END LICENSE

#### What this app should do ####
#TODO: Users should be able to C/R/U/D Text Files
#TODO:


import gettext
from gettext import gettext as _
gettext.textdomain('text-editor')

from gi.repository import Gtk # pylint: disable=E0611
import logging
logger = logging.getLogger('text_editor')

from text_editor_lib import Window
from text_editor.AboutTextEditorDialog import AboutTextEditorDialog
from text_editor.PreferencesTextEditorDialog import PreferencesTextEditorDialog

# See text_editor_lib.Window.py for more details about how this class works
class TextEditorWindow(Window):
    __gtype_name__ = "TextEditorWindow"

	working_file_path = "" # keep track of the file we are working
    
    def finish_initializing(self, builder): # pylint: disable=E1002
        """Set up the main window"""
        super(TextEditorWindow, self).finish_initializing(builder)

        self.AboutDialog = AboutTextEditorDialog
        self.PreferencesDialog = PreferencesTextEditorDialog
        # Code for other initialization actions should be added here.

	def file_new_handler(self, widget, data=None):
		print "CREATE NEW FILE"
	
	def file_save_handler(self, widget, data=None):
		print "SAVING FILE"

	def file_save_as_handler(self, widget, data=None):
		print "SAVE AS..."

	def file_open_handler(self, widget, data=None):
		print "OPEN FILE"
		dialog = Gtk.FileChooserDialog ("Open File", widget.get_toplevel(), Gtk.FileChooserAction.OPEN);
		dialog.add_button(Gtk.STOCK_CANCEL, 0)
		dialog.add_button(Gtk.STOCK_OK, 1)
		dialog.set_default_response(1)

		f_filter = Gtk.FileFilter()
		f_filter.add_pattern("*.txt")

		dialog.set_filter(f_filter)

		if dialog.run() ==1:
			file_selected =dialog.get_filename()
			# open file, read contents and send to TextBuff
			with open(file_selected) as f:
				data = f.read()
				self._set_text(data)
			self.working_file = file_selected

		dialog.destroy()
	


	#---- helper methods----#
	def _get_text(self):
		""" Returns TextBuffer text"""
		buff = self.builder.get_object("write_view").get_buffer()
		
		return buff.get_text(buff.get_start_iter(), buff.get_end_iter())
	

	def _set_text(self, text):
		""" Set text in TextBuffer"""
		buff = self.builder.get_object("write_view").get_buffer()
		buff.set_text(text)

		return True


	
