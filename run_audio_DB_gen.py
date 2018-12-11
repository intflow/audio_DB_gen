#See https://freesound.org/docs/api/resources_apiv2.html for usage
#Usage : python run_audio_DB_gen.py /



from __future__ import print_function
import os
import sys
import soundfile as sf
import random
import numpy as np


def main():

	#----Parameter Definition----
	HOME_DIR = 'D:/BSsoft/DB_Management'
	TARGET_NAME = 'timit_train'
	INTERF1_NAME = 'woman_scream'
	BGN_NAME = 'DEMAND_PCAFETER'
	MIX_ALIAS = 'TEST1'
	SNR = 0

	TARGET_PATH = HOME_DIR + '/TIMIT/timit/train/all'
	INTERF1_PATH = 'D:/audio_crawl_data/scream_woman/wav'
	BGN_PATH = HOME_DIR + '/DEMAND/PCAFETER'
	OUT_PATH = HOME_DIR + '/' + MIX_ALIAS + '/' + str(SNR)

	num_file_DB = 'whole'
	DB_read_seed = 3

	random.seed( DB_read_seed ) #Initialize random seed

	#----open each target file----
	if not os.path.exists(OUT_PATH):
		os.makedirs(OUT_PATH)

	#----scan noise file lists
	bgn_list = []
	for (path_bgn, dir_bgn, files_bgn) in os.walk(BGN_PATH):
		files_bgn = random.sample(files_bgn, len(files_bgn)) #Randomize file order
		for filename in files_bgn[::1]:
			ext = os.path.splitext(filename)[-1]

			if ext == '.wav':
				bgn_list.append(path_bgn + "/" + filename)
				

	#----scann every target files
	for (path, dir, files) in os.walk(TARGET_PATH):

		#Set number of files to be loaded
		if num_file_DB == 'whole':
			num_file_DB = len(files)
			step = 1 #Load every data
		else:
			step = int(len(files) / num_file_DB)
			if step < 1:
				step = 1      

		for filename in files[::step]:
			ext = os.path.splitext(filename)[-1]

			if ext == '.wav':
				file_path = path + "/" + filename
				(x, fs_x) = sf.read(file_path, dtype='int16') 
				print("----Loading " + filename + ", fs: " + str(fs_x) + "----")
				
				#Randomly choose bgn file and mix points
				bgn_idx = random.randrange(0,len(bgn_list))
				
				#Sample bgn noise file
				(d, fs_d) = sf.read(bgn_list[bgn_idx], dtype='int16')
				
				#select random start position
				bgn_p = random.randrange(0,len(d) - len(x))
				d = d[bgn_p:bgn_p+len(x)]

				#Get noise gain
				P_x = np.sum(np.abs(x))
				P_d = np.sum(np.abs(d))
				alpha = P_x / ( (10 ** (SNR/20)) * P_d)

				#Get Noisy Mixture
				y = x + alpha * d
				y = np.array(y, dtype='int16')
				file_path_out = OUT_PATH + '/' + filename
				sf.write(file_path_out, y, fs_x, 'PCM_16')


if __name__ == '__main__':

	main()
