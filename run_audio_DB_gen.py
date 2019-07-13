#See https://freesound.org/docs/api/resources_apiv2.html for usage
#Usage : python run_audio_DB_gen.py /



from __future__ import print_function
import os
import sys
import soundfile as sf
import random
import numpy as np
import librosa  #need for resampled load
import json
#import resampy


def main(param):

	#----Parameter Definition----
	TARGET_PATH = param['TARGET_PATH']
	OUT_PATH = param['OUT_PATH']
	BGN_PATH_LIST = param['BGN_PATH_LIST']
	BGN_LABEL = param['BGN_LABEL']
	SNR_LIST = param['SNR_LIST']
	TARGET_SAMPLING = param['TARGET_SAMPLING']
	num_file_DB = param['num_file_DB']
	DB_read_seed = param['DB_read_seed']
	SAVE_SEP_REF = param['SAVE_SEP_REF'] #Save true sources of mixture
	OUT_SCALE = param['OUT_SCALE'] #Save true sources of mixture


	random.seed( DB_read_seed ) #Initialize random seed

	if not os.path.exists(OUT_PATH):
		os.makedirs(OUT_PATH)

	for SNR in SNR_LIST:
		bgn_id = 0
		for BGN_PATH in BGN_PATH_LIST:

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
					step = int(len(files) / (num_file_DB-1))
					if step < 1:
						step = 1      

				for filename in files[::step]:
					ext = os.path.splitext(filename)[-1]

					if ext == '.wav':
						file_path = path + "/" + filename
						(x, fs_x) = librosa.load(file_path, sr=TARGET_SAMPLING)
						#(x, fs_x) = sf.read(file_path, dtype='int16') 
						#x_hat = resampy.resample(x, fs_x, TARGET_SAMPLING)
						print("----Loading " + filename + ", fs: " + str(TARGET_SAMPLING) + "----")
						
						#Randomly choose bgn file and mix points
						bgn_idx = random.randrange(0,len(bgn_list))
						
						#Sample bgn noise file
						(d, fs_d) = librosa.load(bgn_list[bgn_idx], sr=TARGET_SAMPLING)
						#(d, fs_d) = sf.read(bgn_list[bgn_idx], dtype='int16')
						#d_hat = resampy.resample(d, fs_d, TARGET_SAMPLING)

						#select random start position
						bgn_p = random.randrange(0,len(d) - len(x))
						d = d[bgn_p:bgn_p+len(x)]

						#Get noise gain
						P_x = np.sum(np.abs(x))
						P_d = np.sum(np.abs(d))
						alpha = P_x / ( (10 ** (SNR/20)) * P_d)

						#Scale Output signals
						x *= OUT_SCALE
						d *= OUT_SCALE

						#Get Noisy Mixture'
						y = x + alpha * d
						y = y * 32768
						y = np.array(y, dtype='int16')

						#if GEN_BY_SNR == 0:
						filename = '_' + str(SNR) + '_'  + str(BGN_LABEL[bgn_id]) + '_' + filename

						file_path_out = OUT_PATH + '/' + filename
						sf.write(file_path_out, y, TARGET_SAMPLING, 'PCM_16')
						
						if SAVE_SEP_REF:
							if not os.path.exists(OUT_PATH + '/target'):
								os.makedirs(OUT_PATH + '/target')
							if not os.path.exists(OUT_PATH + '/noise'):
								os.makedirs(OUT_PATH + '/noise')

							x = np.array(x * 32768, dtype='int16')
							d = np.array(alpha * d * 32768, dtype='int16')
							file_path_out = OUT_PATH + '/target/' + filename
							sf.write(file_path_out, x, fs_x, 'PCM_16')
							file_path_out = OUT_PATH + '/noise/' + filename
							sf.write(file_path_out, d, fs_x, 'PCM_16')

			bgn_id += 1

if __name__ == '__main__':

	json_param = open('configs/TIMIT_test_TAUnet.json').read()
	param = json.loads(json_param)
	main(param)
