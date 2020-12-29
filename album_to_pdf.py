import os
import photos
import console
import dialogs		
from tempfile import NamedTemporaryFile
from PyPDF2 import PdfFileReader, PdfFileWriter

'''
In this program the following things will be done:
	
	- The user will choose one or more albums to make into a PDF and share it with Pythonista's built in share sheet.
		* The pdf file will be named after the album used to make it
	
	- The Program will compile all images (except for those with transparent backgrounds for some reason as they crash the program) into a single pdf file.
	
	- Afterwards it will ask the user if they would like to delete the pictures.

'''

class Selection_Handler:
	data = {album.title:album for album in photos.get_albums()}
	
	@property
	def names(self):
		return list(self.data.keys())
	
	@property
	def albums(self):
		return [self.data[selection] for selection in self.selections]
	
	#here we sort theough and remove every photo album that has no pictures in them, as selecting one would crash the program when it tries to make a PDF from it's nonexistant images
	def filter_albums(self):
		albums_to_remove = list()
		for name, album in self.data.items():
			if len(album.assets) == 0:
				albums_to_remove.append(name)
		[self.data.pop(album) for album in albums_to_remove]
		
	def make_selection(self):
		self.filter_albums()
		self.selections = dialogs.list_dialog('Galleries',self.names,True)
		
def get_images(album):
	return [asset.get_image() for asset in album.assets]


if __name__ == '__main__':
	handler = Selection_Handler()
	
	handler.make_selection()
	
	#here we make a 2-staged for loop making a tempfile for each individual image and adding each to the pdf file we will be sharing
	for album in handler.albums:
		pdf_writer = PdfFileWriter()
		for image in get_images(album):
			file = NamedTemporaryFile('wb')
			image.save(file.file,'PDF')
			pdf_file_data = PdfFileReader(file.name)
			pdf_writer.addPage(pdf_file_data.getPage(0))
		file_name = album.title+'.pdf'
		pdf_writer.write(open(file_name,'wb'))
		
		#here we will be able to share the pdf with any app/person that would be able to recieve them.
		console.open_in(file_name)
		
		#since I have made the program in such a way that the PDF is named after the album that was used to create it I have to manually remove the file since you can't directly name a temporary filew
		os.remove(file_name)
		
		title = 'Delete Pictures?'
		choices = ['Yes','No']
		delete_pics = dialogs.list_dialog(title=title,items=choices)
		if delete_pics == 'Yes':
			photos.batch_delete(album.assets)
		
		
