#!/usr/bin/env python3

import os, sys
import boto3
import datetime
import dateutil.parser
from utils import read_hash_record, update_hash_record
import logging

logging.basicConfig(stream=sys.stdout, level=logging.INFO, format="%(message)s")

hash_record_path = '/tmp/collect_record.txt'
audio_bucket = 'hackathon-podcast-search'
transcript_bucket = 'hackathon-podcast-search-transcript'

def find_new_objects(bucket, max_age):
	"""
	Returns all s3 keys (objects) newer than max-age hours in the passed bucket object, as a
	list of boto.s3.key.Key objects.
	"""
	s3 = boto3.client('s3')
	res = s3.list_objects_v2(Bucket=bucket)

	if res is None or 'Contents' not in res:
		return []

	objects = res['Contents']

	past_time_at_max_age = datetime.datetime.now() - datetime.timedelta(hours=max_age)

	# timestamp is ISO-8601, i.e. 2013-01-04T17:49:51.000Z. dateutil.parser handles it.

	return [ key for key in objects if key['LastModified'].replace(tzinfo=None) > past_time_at_max_age ]


new_files = find_new_objects(audio_bucket, 24)

if not new_files:
	exit()

transcribe = boto3.client('transcribe')
file_record = read_hash_record(hash_record_path)
worked_list = []

for file in new_files:
	file_name = os.path.splitext(file['Key'])[0]
	file_hash = file_name +'_'+file['ETag'][1:-1]
	job_uri = 's3://'+audio_bucket+'/'+file['Key']
	if file_hash not in file_record:
		try:
			transcribe.start_transcription_job(
				TranscriptionJobName = file_hash,
				Media = {'MediaFileUri': job_uri},
				MediaFormat ='mp3',
				LanguageCode ='en-US',
				OutputBucketName = transcript_bucket,
			)
		except transcribe.exceptions.ConflictException as e:
			if e.response['Error']['Code'] == 'ConflictException':
				logging.info('Job ['+file_hash+'] is already running.')
			else:
				logging.info("Unexpected error: %s" % e)
		worked_list.append(file_hash)

print("Submitted jobs:", worked_list)
update_hash_record(worked_list, hash_record_path)
