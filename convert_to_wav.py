import os

def all_to_wave(dirname, sr, ch):
	filenames = os.listdir(dirname)
	for (path, dir, files) in os.walk(dirname):
		for filename in files:
			ext = os.path.splitext(filename)[-1]
			if ext != '.ini':
				filename2 = filename[:-1*len(ext)]
				filename = path + "\\" + filename
				filename2 = path + "\\wav\\" + filename2
				
				#Make subfolder
				if not os.path.exists(path + "\\wav"):
					os.makedirs(path + "\\wav")
				options = " -ar " + str(sr) + " -ac " + str(ch)
				print("ffmpeg.exe -i "+ filename + options + " " + filename2 + ".wav")
				os.system("ffmpeg.exe -i "+ filename + options + " " + filename2 + ".wav")
			
