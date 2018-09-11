#See https://freesound.org/docs/api/resources_apiv2.html for usage
#Usage : python run_audio_DB_gen.py \
#			--audio_crawling_freesound=1 \
#			--target_query="scream woman" \
#			--target_name="scream_woman"


from __future__ import print_function
import freesound
import os
import sys
import argparse
from convert_to_wav import all_to_wave
from annot_VAD import annot_VAD

FLAGS = None

#Set freesound API and OAuth Keys
os.environ['FREESOUND_API_KEY'] = "XCeupOeAd0MWlTwm5wS1r0WIov7vRGsQgLlL6uHD"
os.environ['FREESOUND_OAUTH_KEY'] = "5zhz3WYJQ9feGliFrhjSCN3p4Zzljl"
api_key = os.getenv('FREESOUND_API_KEY', None)
oauth_key = os.getenv('FREESOUND_OAUTH_KEY', None)
if api_key is None:
	print("You need to set your API key as an evironment variable",)
	print("named FREESOUND_API_KEY")
	sys.exit(-1)

#Choose token or oauth (oauth is required for retrieve source files
freesound_client = freesound.FreesoundClient()
freesound_client.set_token(token = api_key, auth_type="token")
#freesound_client.set_token(token = oauth_key, auth_type="oauth")


def main():
	
	home_dir = FLAGS.home_dir
	target_name = FLAGS.target_name
	# Query by text
	if FLAGS.audio_crawling_freesound == 1:
		target_query = FLAGS.target_query
		if not os.path.exists(home_dir+"/"+target_name):
			os.makedirs(home_dir+"/"+target_name)
		print("Searching for " + target_query + ":")
		print("----------------------------")
		results_pager = freesound_client.text_search(
			query=target_query,
			filter="duration:[0.5 TO 5.0]",
			sort="score",
			fields="id,name,previews,username"
		)
		page = 1
		file_num = 1
		while results_pager.count > 0:
			print("Num results:", results_pager.count)
			print("\t----- PAGE ",page,"-----")
			for sound in results_pager:
				print("\t-", sound.name, "by", sound.username)
				name, ext = os.path.splitext(sound.name)
				if ext == '' or ext == ' ' or ext[-1]=="\"":
					ext = '.wav'
				#sound.retrieve(directory=home_dir+"/"+target_name, name=target_name+"_"+str(file_num)+ext)
				sound.retrieve_preview(directory=home_dir+"/"+target_name, name=target_name+"_"+str(file_num)+ext)
				file_num = file_num + 1
			try:
				results_pager = results_pager.next_page()
			except:
				print("----- Download Completed!!! -----")
				break
			page = page + 1

	#Reformat to Target sampling rate, channel, sampl bit
	if FLAGS.reformat_FFMPEG == 1:
		all_to_wave(dirname=home_dir+"/"+target_name, sr=FLAGS.reformat_sr, ch=FLAGS.reformat_ch)

	#Annotate active region by VAD
	if FLAGS.annot_VAD == 1:
		annot_VAD(dirname=home_dir+"/"+target_name+"/wav")
	
if __name__ == '__main__':
	parser = argparse.ArgumentParser()
	parser.add_argument(
		'--home_dir',
		type=str,
		default='/audio_gen_data',
		help='root directory for DB generation')
	parser.add_argument(
		'--target_query',
		type=str,
		default='scream woman',
		help='Query keywords')
	parser.add_argument(
		'--target_name',
		type=str,
		default='scream_woman',
		help='Where to download the queried audio files')
	parser.add_argument(
		'--audio_crawling_freesound',
		type=int,
		default=1,
		help='Turn on/off audio data crawling from freesound')
	parser.add_argument(
		'--reformat_FFMPEG',
		type=int,
		default=1,
		help='Turn on/off audio reformatting using FFMPEG')
	parser.add_argument(
		'--annot_VAD',
		type=int,
		default=1,
		help='Annotate start-end times by VAD')
	parser.add_argument(
		'--reformat_sr',
		type=int,
		default=16000,
		help='target sampling rate after reformatting')
	parser.add_argument(
		'--reformat_ch',
		type=int,
		default=1,
		help='target channel after reformatting')
	parser.add_argument(
		'--reformat_bit',
		type=int,
		default=16,
		help='target sample bit after reformatting')
		
		
	FLAGS, unparsed = parser.parse_known_args()
	main()
## Get sound info example
#print("Sound info:")
#print("-----------")
#sound = freesound_client.get_sound(96541)
#print("Getting sound:", sound.name)
#print("Url:", sound.url)
#print("Description:", sound.description)
#print("Tags:", " ".join(sound.tags))
#print()
#
## Get sound info example specifying some request parameters
#print("Sound info specifying some request parameters:")
#print("-----------")
#sound = freesound_client.get_sound(
#	96541,
#	fields="id,name,username,duration,analysis",
#	descriptors="lowlevel.spectral_centroid",
#	normalized=1
#)
#print("Getting sound:", sound.name)
#print("Username:", sound.username)
#print("Duration:", str(sound.duration), "(s)")
#print("Spectral centroid:",)
#print(sound.analysis.lowlevel.spectral_centroid.as_dict())
#print()
#
#
## Get sound analysis example
#print("Get analysis:")
#print("-------------")
#analysis = sound.get_analysis()
#
#mfcc = analysis.lowlevel.mfcc.mean
#print("Mfccs:", mfcc)
## you can also get the original json (this apply to any FreesoundObject):
#print(analysis.as_dict())
#print()
#
## Get sound analysis example specifying some request parameters
#print("Get analysis with specific normalized descriptor:")
#print("-------------")
#analysis = sound.get_analysis(
#	descriptors="lowlevel.spectral_centroid.mean",
#	normalized=1
#)
#spectral_centroid_mean = analysis.lowlevel.spectral_centroid.mean
#print("Normalized mean of spectral centroid:", spectral_centroid_mean)
#print()
#
## Get similar sounds example
#print("Similar sounds: ")
#print("---------------")
#results_pager = sound.get_similar()
#for similar_sound in results_pager:
#	print("\t-", similar_sound.name, "by", similar_sound.username)
#print()
#
## Get similar sounds example specifying some request parameters
#print("Similar sounds specifying some request parameters:")
#print("---------------")
#results_pager = sound.get_similar(
#	page_size=10,
#	fields="name,username",
#	descriptors_filter="lowlevel.pitch.mean:[110 TO 180]"
#)
#for similar_sound in results_pager:
#	print("\t-", similar_sound.name, "by", similar_sound.username)
#print()

#
## Content based search example
#print("Content based search:")
#print("---------------------")
#results_pager = freesound_client.content_based_search(
#	descriptors_filter="lowlevel.pitch.var:[* TO 20]",
#	target_query='lowlevel.pitch_salience.mean:1.0 lowlevel.pitch.mean:440'
#)
#
#print("Num results:", results_pager.count)
#for sound in results_pager:
#	print("\t-", sound.name, "by", sound.username)
#print()
#
## Getting sounds from a user example
#print("User sounds:")
#print("-----------")
#user = freesound_client.get_user("Jovica")
#print("User name:", user.username)
#results_pager = user.get_sounds()
#print("Num results:", results_pager.count)
#print("\t----- PAGE 1 -----")
#for sound in results_pager:
#	print("\t-", sound.name, "by", sound.username)
#print("\t----- PAGE 2 -----")
#results_pager = results_pager.next_page()
#for sound in results_pager:
#	print("\t-", sound.name, "by", sound.username)
#print()
#
#
## Getting sounds from a user example specifying some request parameters
#print("User sounds specifying some request parameters:")
#print("-----------")
#user = freesound_client.get_user("Jovica")
#print("User name:", user.username)
#results_pager = user.get_sounds(
#	page_size=10,
#	fields="name,username,samplerate,duration,analysis",
#	descriptors="rhythm.bpm"
#)
#
#print("Num results:", results_pager.count)
#print("\t----- PAGE 1 -----")
#for sound in results_pager:
#	print("\t-", sound.name, "by", sound.username,)
#	print(", with sample rate of", sound.samplerate, "Hz and duration of",)
#	print(sound.duration, "s")
#print("\t----- PAGE 2 -----")
#results_pager = results_pager.next_page()
#for sound in results_pager:
#	print("\t-", sound.name, "by", sound.username,)
#	print(", with sample rate of", sound.samplerate, "Hz and duration of",)
#	print(sound.duration, "s")
#print()
#
## Getting sounds from a pack example specifying some request parameters
#print("Pack sounds specifying some request parameters:")
#print("-----------")
#pack = freesound_client.get_pack(3524)
#print("Pack name:", pack.name)
#results_pager = pack.get_sounds(
#	page_size=5,
#	fields="id,name,username,duration,analysis",
#	descriptors="lowlevel.spectral_flatness_db"
#)
#print("Num results:", results_pager.count)
#print("\t----- PAGE 1 -----")
#for sound in results_pager:
#	print("\t-", sound.name, "by", sound.username, ", with duration of",)
#	print(sound.duration, "s and a mean spectral flatness of",)
#	print(sound.analysis.lowlevel.spectral_flatness_db.mean)
#print("\t----- PAGE 2 -----")
#results_pager = results_pager.next_page()
#for sound in results_pager:
#	print("\t-", sound.name, "by", sound.username, ", with duration of",)
#	print(sound.duration, "s and a mean spectral flatness of",)
#	print(sound.analysis.lowlevel.spectral_flatness_db.mean)
#print()
#
## Getting bookmark categories from a user example
#print("User bookmark categories:")
#print("-----------")
#user = freesound_client.get_user("frederic.font")
#print("User name:", user.username)
#results_pager = user.get_bookmark_categories(page_size=10)
#print("Num results:", results_pager.count)
#print("\t----- PAGE 1 -----")
#for bookmark_category in results_pager:
#	print("\t-", bookmark_category.name, "with", bookmark_category.num_sounds,)
#	print("sounds at", bookmark_category.url)
#print()
