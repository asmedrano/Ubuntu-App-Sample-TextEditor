# -*- Mode: Python; coding: utf-8; indent-tabs-mode: nil; tab-width: 4 -*-
### BEGIN LICENSE
# This file is in the public domain
### END LICENSE

#### What this app should do ####
#TODO: Handle Exiting or creating new if changes are in buffer and file is not saved
#TODO: Files are only able to be appended to :( need to fix this :D

import gettext
from gettext import gettext as _
gettext.textdomain('text-editor')

from gi.repository import Gtk, Gdk # pylint: disable=E0611
import logging
logger = logging.getLogger('text_editor')

from text_editor_lib import Window
from text_editor.AboutTextEditorDialog import AboutTextEditorDialog
from text_editor.PreferencesTextEditorDialog import PreferencesTextEditorDialog

from text_editor.widget_text_editor import TextEditor

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
		
		self.clipboard = Gtk.Clipboard.get(Gdk.SELECTION_CLIPBOARD)
		self.clipboard.clear()
		
		# create editor
		self.editor = TextEditor()
		self.editor.set_wrap_mode(Gtk.WrapMode.WORD_CHAR)
		self.editor.set_pixels_above_lines(2)
		self.editor.set_pixels_below_lines(2)
		self.editor.set_pixels_inside_wrap(4)
		self.editor.set_left_margin(10)
		self.editor.set_right_margin(10)
		self.editor.show()
		self.builder.get_object("hbox1").pack_start(self.editor, True, True,1)

	def on_destroy(self, widget, data=None):
		"""override the on_destroy() method so we can add in some pre close logic to our app
		   At its most Basic, we could do this
		   super(TextEditorWindow, self).on_destroy(widget)
		   and the app would close as normal
		"""
		buff = self._get_buffer()
		if buff.get_modified() == True:
			if self.show_changes_dialog(widget) == 1:
				self.save_buffer_to_file(widget)
		
		super(TextEditorWindow, self).on_destroy(widget)

	def file_new_handler(self, widget, data=None):
		""" Resets TextBuffer
		"""
		buff = self._get_buffer()
		if buff.get_modified() == True:
			if self.show_changes_dialog(widget) == 1:
				self.save_buffer_to_file(widget)
		
		buff.delete(buff.get_start_iter(), buff.get_end_iter())
		# also reset the working_file_path
		self.working_file_path=""
		
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
				f = open(self.working_file_path, "r+")
				buff = self._get_buffer()
				
				f.seek(0)
				f.truncate()
				f.write(self._get_text())

				#update modified flag
				buff.set_modified(False)
				
				f.close()

			except IOError as e:
				print "COULDNT OPEN FILE"
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
			if self.show_changes_dialog(widget) == 1:
				print "User Hits ok"
				self.save_buffer_to_file(widget)
		
		self.show_file_chooser(buff, widget)

	def show_file_chooser(self,buff, widget, data=None):

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
	

	def copy_to_clipboard(self, widget, data=None):
		""" Copy selected text to clipboard"""
		#print "Copying text"
		buff = self._get_buffer()
		buff.copy_clipboard(self.clipboard)
	
	def cut_to_clipboard(self, widget, data=None):
		""" Cut selected text to clipboard"""
		#print "Copying text"
		buff = self._get_buffer()
		buff.cut_clipboard(self.clipboard, True)

	def paste_from_clipboard(self, widget, data=None):
		""" Paste from Clipboard """
		#print "Pasting from clipboard"
		buff = self._get_buffer()
		buff.paste_clipboard(self.clipboard, None, True)
	
	
	def undo_action_handler(self, widget, data=None):
		self.editor.undo()

	
	def _on_window_destroy(self, widget, data=None):
		self.check_close(widget)
		
	def show_changes_dialog(self,widget):
		"""Opens a dialog that informs the user that there are changes to be saved """
		dialog = Gtk.MessageDialog(widget.get_toplevel())
		dialog.set_default_size(310, 60)
		dialog.format_secondary_text("Save changes to file?")
		dialog.add_button(Gtk.STOCK_NO, 0)
		dialog.add_button(Gtk.STOCK_YES, 1)
		dialog.set_default_response(1)
		

		if dialog.run() == 1:
			dialog.destroy()
			return 1
		else:
			dialog.destroy()
			return 0

		


	#---- helper methods----#
	
	def _get_buffer(self):
		"""returns main TextBuffer"""
		return self.editor.get_buffer()

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
	
