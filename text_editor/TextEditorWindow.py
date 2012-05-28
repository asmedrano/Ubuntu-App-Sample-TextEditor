# -*- Mode: Python; coding: utf-8; indent-tabs-mode: nil; tab-width: 4 -*-
### BEGIN LICENSE
# This file is in the public domain
### END LICENSE

#### What this app should do ####
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
    working_file_name = "Untitled"

    def finish_initializing(self, builder): # pylint: disable=E1002
        """Set up the main window"""
        super(TextEditorWindow, self).finish_initializing(builder)

        self.AboutDialog = AboutTextEditorDialog
        self.PreferencesDialog = PreferencesTextEditorDialog
        # Code for other initialization actions should be added here.

	def file_new_handler(self, widget, data=None):
		""" Resets TextBuffer
		"""
		print "CREATE NEW FILE"

		buff = self._get_buffer()
		if buff.get_modified() == True:
			print "There are changes, should we save them?"
		else:
			# clear out the buffer
			buff.delete(buff.get_start_iter(), buff.get_end_iter())

		
	def file_save_handler(self, widget, data=None):
		print "SAVING FILE"
		self.save_buffer_to_file(widget)
	
	def save_buffer_to_file(self, widget):
		""" Save working_file to disk
			If we havent assigned working_file_path, this is a new file and we need to do the save AS routine
		"""
		if self.working_file_path == "":
			self.save_buffer_to_file_AS(widget)
		else:
			try:
				f = open(self.working_file_path, "rw")
				buff = self._get_buffer()
				f.writelines(self._get_text())
				#update modified flag
				buff.set_modified(False)
				f.close()

			except IOError as e:
				self.save_buffer_to_file_AS(widget)


	def file_save_as_handler(self, widget, data=None):
		""" Called when user selects, "Save As" """
		print "SAVE AS..."
		self.save_buffer_to_file_AS(widget)
	
	
	def save_buffer_to_file_AS(self, widget):
		""" Brings up Save As Dialog """
		
		dialog = Gtk.FileChooserDialog ("Save File As", widget.get_toplevel(), Gtk.FileChooserAction.SAVE);
		dialog.add_button(Gtk.STOCK_CANCEL, 0)
		dialog.add_button(Gtk.STOCK_OK, 1)
		dialog.set_default_response(1)

		if dialog.run() == 1:
			file_selected = dialog.get_filename()
			self.working_file_path = file_selected
			buff = self._get_buffer()
			
			with open(self.working_file_path,"w") as f:
				f.writelines(self._get_text())

			#update modified flag
			buff.set_modified(False)
		dialog.destroy()


	def file_open_handler(self, widget, data=None):
		""" Opens an existing file. 
			Checks to see if the buffer has been modified before opening it. 
		"""

		buff = self._get_buffer()
		if buff.get_modified() == True:
			print "There are changes, should we save them?"
		else:
			# clear out the buffer

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
					buff.delete(buff.get_start_iter(), buff.get_end_iter())
					buff.set_text(data)
					buff.set_modified(False)

				self.working_file_path = file_selected
			
			dialog.destroy()
	

	#---- helper methods----#

	def _get_buffer(self):
		"""returns main TextBuffer"""
		return self.builder.get_object("write_view").get_buffer()

	def _get_text(self):
		""" Returns TextBuffer text"""
		buff = self._get_buffer()
		start_iter = buff.get_start_iter()
		end_iter = buff.get_end_iter()
		
		return buff.get_text(start_iter, end_iter, False)

	def _set_text(self, text):
		""" Set text in TextBuffer"""
		buff = self._get_buffer()
		buff.set_text(text)
		return True
	
