import subprocess
import exifread
from PIL import Image


def extract_table(filename):
	p = subprocess.Popen(['djpeg','-verbose','-verbose','-verbose',filename], 
		stdout=subprocess.PIPE, 
		stderr=subprocess.PIPE)
	out,info_jpeg = p.communicate() #djpeg returns q-tables in stderr

	lines = info_jpeg.split('\n')
	tmp = []
	jpeg_structure = []

	for i in range(len(lines)):
		if lines[i] == 'Start of Image':
			jpeg_structure.append('SOI')
		elif lines[i] == 'Define Quantization Table 0  precision 0':
			jpeg_structure.append('DEF-QT0')
			for j in range(i+1,i+9):
				a = lines[j].split('  ')
				for s in a:
					t = s.translate(None,' ')
					if t != '':
						tmp.append(t)

		elif lines[i] == 'Define Quantization Table 1  precision 0':
			jpeg_structure.append('DEF-QT1')
			for j in range(i+1,i+9):
				a = lines[j].split('  ')
				for s in a:
					t = s.translate(None,' ')
					if t != '':
						tmp.append(t)
		elif 'Start Of Frame' in lines[i]:
			jpeg_structure.append('SOF')
		elif 'Define Huffman Table' in lines[i]:
			jpeg_structure.append('DEF-HT')
		elif 'Start Of Scan' in lines[i]:
			a = lines[i].split(' ')
			jpeg_structure.append('SOS:'+a[3])
		elif 'End Of Image' in lines[i]:
			jpeg_structure.append('EOI')

	if len(tmp) < 128:
		for i in range(len(tmp),128):
			tmp.append(0)
	tmp = [int(coeff_value) for coeff_value in tmp]

	return tmp,jpeg_structure

def feature_extractor(filename):
	features = []
	qtable,jpeg_structure = extract_table(filename)
	im = Image.open(filename)
	width, height = im.size

	# Open image file for reading (binary mode)
	f = open(filename, 'rb')
	# Return Exif tags
	tags = exifread.process_file(f)

	features = [width, height, len(tags)]

	for coefficient in qtable:
		features.append(coefficient)

	features.append(len(jpeg_structure))

	return features,tags
