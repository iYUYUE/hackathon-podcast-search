import os

def read_hash_record(hash_record_path):
	if not os.path.exists(hash_record_path):
		return []
	with open(hash_record_path, 'r') as f:
		l = [line.rstrip('\n') for line in f]
		return l

def update_hash_record(l, hash_record_path):
	with open(hash_record_path, 'a') as f:
		for item in l:
			f.write("%s\n" % item)