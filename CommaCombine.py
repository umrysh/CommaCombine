#!/usr/bin/python
# -*- coding: utf-8 -*-

#    Built for python 2.7

#    Copyright 2012 Dave Umrysh
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.


import pygtk,gtk,csv,operator
pygtk.require('2.0')

arr = []

class mainScreen():
	def __init__(self):
		self.viewMainScreen()
	def fileselect(self, widget, entryLOC):
		dialog = gtk.FileChooserDialog("Open..",
			None,
			gtk.FILE_CHOOSER_ACTION_OPEN,
			(gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL,
			gtk.STOCK_OPEN, gtk.RESPONSE_OK))
		dialog.set_default_response(gtk.RESPONSE_OK)
		dialog.set_select_multiple(True)

		filter = gtk.FileFilter()
		filter.set_name("CSV")
		filter.add_pattern("*.csv")
		dialog.add_filter(filter)
		response = dialog.run()
		if response == gtk.RESPONSE_OK:
			self.csvpath = dialog.get_filenames()
			if len(self.csvpath) >1:
				entryLOC.set_text("%s Files Selected." % len(self.csvpath))
			else:
				entryLOC.set_text(self.csvpath[0])
		dialog.destroy()
	def addCSV(self,widget,fileName):
		### Test for blank and zero values
		if 	fileName.get_text() != "":
			global arr
			for count in range (0,len(self.csvpath)):
				arr.append(self.csvpath[count])
			self.rebuild()
	def deleteCSV(self,widget,count):
		global arr
		arr.pop(count)
		self.rebuild()
	def rebuild(self):
		global arr
		self.hbox3.destroy()
		self.hbox4.destroy()

		self.hbox3 = gtk.HBox(False, 0)
		self.select_vbox.pack_start(self.hbox3, False, True, 5)

		prevSelect_vbox = gtk.VBox(False, 5)
		self.hbox3.pack_start(prevSelect_vbox, True, True, 0)


		self.hbox4 = gtk.HBox(False, 0)
		self.select_vbox.pack_start(self.hbox4, False, True, 5)
		
		for count in range(0,len(arr)):
			prevhbox3 = gtk.HBox(False, 0)
			prevSelect_vbox.pack_start(prevhbox3, False, True, 5)

			
			if len(arr[count])>40:
				existing1 = gtk.Label("...%s" % arr[count][-40:])
			else:
				existing1 = gtk.Label(arr[count])

			existingButton = gtk.Button("Del ")
			existingButton.connect("clicked", self.deleteCSV,count)
			prevhbox3.pack_end(existingButton, False, True, 5)

			existing1.set_alignment(0.5, 0.5)
			existing1.set_line_wrap(True)
			prevhbox3.pack_end(existing1, True, True, 0)

		####Add new####
		button = gtk.Button("Select CSV file")
		entryLOC = gtk.Entry()
		entryLOC.set_text("")
		entryLOC.set_editable(False)
		button.connect("clicked", self.fileselect, entryLOC)
		self.hbox4.pack_start(button, False, False, 0)
		self.hbox4.pack_start(entryLOC, False, False, 0)

		button1 = gtk.Button("Add")
		button1.connect("clicked", self.addCSV,entryLOC)
		self.hbox4.pack_start(button1, True, True, 5)

		self.hbox3.show_all()
		self.hbox4.show_all()
	def combine(self,widget):
		### On submit load all the CSV's into an array ###
		self.dataArray = []
		removeheadings = self.removeHeadingsCheck.get_active()

		for count in range(0,len(arr)):
			# Open the selected file #
			Ofile = open('%s' % arr[count], 'r')
			Reader = csv.reader(Ofile, delimiter=',', quotechar='"')

			startFile=True
			for row in Reader:
				### Check if we are to remove headings ###
				if startFile and removeheadings and count != 0:
					startFile = False
				else:
					### Add to array#####
					a = []
					for counter in range(0,len(row)):
						a.append(row[counter])
					self.dataArray.append(a)

		if len(self.dataArray) != 0:
			### In case the user submitted no CSVs ###
			### Sort the array ###
			if self.sortCheck.get_active():
				### Check if user gave a valid column
				if self.sortspinner.get_value_as_int() <= len(self.dataArray[0]):
					### We can sort ###
					### Check if we are to remove the first row
					if self.sort2Check.get_active():
						a = self.dataArray[0]
						self.dataArray.pop(0)
						self.dataArray = sorted(self.dataArray, key=operator.itemgetter(self.sortspinner.get_value_as_int()-1))
						self.dataArray.insert(0,a)
					else:
						self.dataArray = sorted(self.dataArray, key=operator.itemgetter(self.sortspinner.get_value_as_int()-1))
			### Open Dialog asking user where they would like the new CSV stored ###
			dialog = gtk.FileChooserDialog(title=None,action=gtk.FILE_CHOOSER_ACTION_SAVE,buttons=(gtk.STOCK_CANCEL,gtk.RESPONSE_CANCEL,gtk.STOCK_OPEN,gtk.RESPONSE_OK))
			dialog.set_current_name("Output.csv")
			dialog.set_default_response(gtk.RESPONSE_OK)
			response = dialog.run()
			if response == gtk.RESPONSE_OK:
				outputpath = dialog.get_filename()
			else:
				outputpath = ""
			dialog.destroy()

			if outputpath != "":
				### Write data to file ###
				f = csv.writer(open(outputpath, 'wb'), delimiter=',',quotechar='"', quoting=csv.QUOTE_MINIMAL)
				for count in range(0,len(self.dataArray)):
					f.writerow(self.dataArray[count])
				dialog = gtk.MessageDialog(window, gtk.DIALOG_MODAL,gtk.MESSAGE_INFO, gtk.BUTTONS_OK,"Combine Completed!")
				dialog.set_title("CommaCombine :)")

				dialog.run()
				dialog.destroy()
		### Send back to main screen ###
	def viewMainScreen(self):
		### Show window so user can select the CSV's to combine. Allow User to add more rows as nessasary ###
		### Also ask user which column number the data should be sorted by ###
		global window
		window = gtk.Window(gtk.WINDOW_TOPLEVEL)
		window.connect("destroy", lambda w: gtk.main_quit())
		window.set_title("CommaCombine - Select Files")
		window.set_default_size(100, 50)
		window.set_property("allow-grow", 0)
		window.set_position(gtk.WIN_POS_CENTER)

		main_vbox = gtk.VBox(False, 5)
		main_vbox.set_border_width(10)
		window.add(main_vbox)

		hbox = gtk.HBox(False, 0)
		main_vbox.pack_start(hbox, False, True, 5)

		# top labels
		Toplabel = gtk.Label("Select CSVs to Combine.")
		Toplabel.set_alignment(0.5, 0.5)
		Toplabel.get_settings().set_string_property('gtk-font-name', 'serif 10','');
		Toplabel.set_line_wrap(True)
		hbox.pack_start(Toplabel, True, True, 0)


		#scrolled selectionbox

		scrolled_vbox = gtk.VBox(False, 5)
		viewport = gtk.Viewport()
		viewport.add(scrolled_vbox)
		sw = gtk.ScrolledWindow()
		sw.add(viewport)
		sw.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
		sw.set_size_request(400, 200)
		viewport.set_shadow_type(gtk.SHADOW_NONE)
		main_vbox.pack_start(sw, False, True, 0)


		frame = gtk.Frame("")
	  
		self.select_vbox = gtk.VBox(False, 5)
		scrolled_vbox.pack_start(frame, False, False, 0)
		frame.add(self.select_vbox)

		self.hbox3 = gtk.HBox(False, 0)
		self.hbox4 = gtk.HBox(False, 0)

		####Extra#####
		self.removeHeadingsCheck = gtk.CheckButton()
		self.removeHeadingsCheck.set_active(True)
		
		removeHeadingslabel = gtk.Label("Remove the first row from subsequent files.")
		removeHeadingslabel.set_alignment(0.5, 0.5)
		removeHeadingslabel.set_line_wrap(True)

		removeHeadings_hbox = gtk.HBox(False, 5)
		main_vbox.pack_start(removeHeadings_hbox, True, False, 0)
		removeHeadings_hbox.pack_start(self.removeHeadingsCheck, False, False, 0)
		removeHeadings_hbox.pack_start(removeHeadingslabel, False, False, 0)

		####Extra2#####
		self.sortCheck = gtk.CheckButton()
		self.sortCheck.set_active(False)
		
		sortlabel = gtk.Label("Sort data using column:")
		sortlabel.set_alignment(0.5, 0.5)
		sortlabel.set_line_wrap(True)


		adj = gtk.Adjustment(6, 1.0, 999999.0, 1.0, 5.0, 0.0)
		self.sortspinner = gtk.SpinButton(adj, 0, 0)
		self.sortspinner.set_wrap(True)

		sort2label = gtk.Label("Do not sort first row as this contains the headings.")
		sort2label.set_alignment(0.5, 0.5)
		sort2label.set_line_wrap(True)

		sort2spacer = gtk.Label("     ")

		self.sort2Check = gtk.CheckButton()
		self.sort2Check.set_active(False)

		sort_hbox = gtk.HBox(False, 5)
		sort2_hbox = gtk.HBox(False, 5)

		main_vbox.pack_start(sort_hbox, True, False, 0)
		main_vbox.pack_start(sort2_hbox, True, False, 0)

		sort_hbox.pack_start(self.sortCheck, False, False, 0)
		sort_hbox.pack_start(sortlabel, False, False, 0)
		sort_hbox.pack_start(self.sortspinner, False, False, 0)

		sort2_hbox.pack_start(sort2spacer, False, False, 0)
		sort2_hbox.pack_start(self.sort2Check, False, False, 0)
		sort2_hbox.pack_start(sort2label, False, False, 0)

		####Buttons#####
		importButton = gtk.Button("Combine!")
		importButton.connect("clicked", self.combine)
		
		buttons_hbox = gtk.HBox(False, 5)
		main_vbox.pack_start(buttons_hbox, True, False, 0)
		buttons_hbox.pack_start(importButton, True, False, 0)

		self.rebuild()

		window.show_all()

def main():
	mainScreen()
	gtk.main()
	return 0

if __name__ == "__main__":
	main()