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
	TARGET_NAME = 'WSJ0'
	INTERF1_NAME = 'woman_scream'
	BGN_NAME = 'CHIME3_BGN_ALL(BUS_CAF_PED_STR)_6CH'
	MIX_ALIAS = 'CHIME3_Noisy'
	SNR = 10

	TARGET_PATH = HOME_DIR + '/CHiME3/data/audio/16kHz/isolated/tr05_org'
	INTERF1_PATH = 'D:/audio_crawl_data/scream_woman/wav'
	BGN_PATH = HOME_DIR + '/CHiME3/data/audio/16kHz/background/CHiME3_background_all/CH6'

	num_file_DB = 'whole'
	DB_read_seed = 3
	SAVE_SEP_REF = 1 #Save true sources of mixture
	GEN_BY_SNR = 0 #organize mixtures by SNR-specific folder 
	random.seed( DB_read_seed ) #Initialize random seed

	if GEN_BY_SNR == 1:
		OUT_PATH = HOME_DIR + '/' + MIX_ALIAS + '/' + str(SNR)
	else:
		OUT_PATH = HOME_DIR + '/' + MIX_ALIAS

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
				

	#----scan every target files
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

				#Get Noisy Mixture'
				y = x + alpha * d
				y = np.array(y, dtype='int16')

				if GEN_BY_SNR == 0:
					filename = str(SNR) + '_' + filename

				file_path_out = OUT_PATH + '/' + filename
				sf.write(file_path_out, y, fs_x, 'PCM_16')
				
				if SAVE_SEP_REF:
					if not os.path.exists(OUT_PATH + '/target'):
						os.makedirs(OUT_PATH + '/target')
					if not os.path.exists(OUT_PATH + '/noise'):
						os.makedirs(OUT_PATH + '/noise')

					x = np.array(x, dtype='int16')
					d = np.array(alpha * d, dtype='int16')
					file_path_out = OUT_PATH + '/target/' + filename
					sf.write(file_path_out, x, fs_x, 'PCM_16')
					file_path_out = OUT_PATH + '/noise/' + filename
					sf.write(file_path_out, d, fs_x, 'PCM_16')

if __name__ == '__main__':

	main()
