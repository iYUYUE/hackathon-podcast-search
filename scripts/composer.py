#!/usr/bin/env python3

import os
import errno
import io
import boto3
import json
import requests
from utils import read_hash_record, update_hash_record

def TREC_maker(no, title, desc, content):
	trec_text = '<DOC>\n'
	trec_text += '<DOCNO>'+no+'</DOCNO>\n'
	trec_text += '<TEXT>\n'+title+'\n\n'+desc+'\n\n'+content+'\n</TEXT>\n'
	trec_text += '</DOC>'
	return trec_text

def write_file(filename, text):
	if not os.path.exists(os.path.dirname(filename)):
		try:
			os.makedirs(os.path.dirname(filename))
		except OSError as exc: # Guard against race condition
			if exc.errno != errno.EEXIST:
				raise

	with open(filename, "w") as f:
		f.write(text)

bucket_name = 'hackathon-podcast-search-transcript'
hash_record_path = '/tmp/compose_record.txt'
cache_path = '/tmp/hackathon-podcast-search-source'
index_path = '/tmp/hackathon-podcast-search.idx'

s3 = boto3.resource('s3')
s3_client = boto3.client('s3')
res = s3_client.list_objects(Bucket = bucket_name)

if res is None or 'Contents' not in res:
	exit()

compose_record = read_hash_record(hash_record_path)
worked_list = []

for obj in res['Contents']:
	object_key = obj['Key']
	filename, file_extension = os.path.splitext(object_key)
	if file_extension == '.json' and filename not in compose_record:
		# get transcript
		bytes_buffer = io.BytesIO()
		s3_client.download_fileobj(Bucket=bucket_name, Key=object_key, Fileobj=bytes_buffer)
		byte_value = bytes_buffer.getvalue()
		str_value = byte_value.decode()
		json_data = json.loads(str_value)
		full_text = json_data['results']['transcripts'][0]['transcript']
		# get metadata
		pid = filename.split('_', 1)[0]
		api_url = "https://audio-api.washpost.arcpublishing.com/api/v1/audio/"
		api_url += pid
		r = requests.get(url=api_url)
		metadata = r.json()
		trec_text = TREC_maker(pid, metadata["title"], metadata["shortDescription"], full_text)
		write_file(cache_path+filename+'/.trectext', trec_text)
		worked_list.append(filename)

print("Composed jobs:", worked_list)

if worked_list:
	# update record
	update_hash_record(worked_list, hash_record_path)
	# update cache
	os.system("~/galago-3.16-bin/bin/galago build --indexPath="+index_path+" --inputPath+"+cache_path)
