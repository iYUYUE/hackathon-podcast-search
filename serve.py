from flask import Flask, request, send_from_directory, render_template

def get_count(path):
	import os
	count = 0
	if os.path.exists(path):
		import subprocess
		result = subprocess.check_output(['wc', '-l', path])
		count = int(result.decode("utf-8").split(' ')[0])
	return count

# set the project root directory as the static folder, you can set others.
app = Flask(__name__, static_url_path='')

@app.route("/")
def send_index():
	return render_template('index.html')

@app.route('/js/<path:path>')
def send_js(path):
	return send_from_directory('static/js', path)

@app.route('/css/<path:path>')
def send_css(path):
	return send_from_directory('static/css', path)

@app.route('/api/search', methods=['POST'])
def handle_search():
	query_str = request.form['query']
	from nltk.tokenize import RegexpTokenizer
	tokenizer = RegexpTokenizer(r'\w+')
	query_str = ' '.join(tokenizer.tokenize(query_str))
	import subprocess
	result = subprocess.check_output(['/home/ubuntu/galago-3.16-bin/bin/galago', 'batch-search', '--index=/tmp/hackathon-podcast-search.idx', '--passageQuery=true', '--passageSize=50', '--passageShift=25', '--queryType=simple', '--requested=10', "--query='"+query_str+"'"])
	result_list = result.decode("utf-8").split('\n')
	ret = []
	dedup = []
	for item in result_list:
		val = item.split(' ')
		if len(val) > 3 and val[2] not in dedup:
			val_dict =	{
				"index": val[3],
				"pid": val[2],
				"score": val[4],
				"start": val[6],
				"end": val[7]
			}
			ret.append(val_dict)
			dedup.append(val[2])
	import json
	return json.dumps(ret)

@app.route('/api/stats', methods=['GET'])
def handle_stats():
	collect_record_path = '/tmp/collect_record.txt'
	compose_record_path = '/tmp/compose_record.txt'
	import subprocess
	result = subprocess.check_output(['/home/ubuntu/galago-3.16-bin/bin/galago', 'stats', '--index=/tmp/hackathon-podcast-search.idx'])
	collect_count = 0
	import json
	ret = json.loads(result)
	ret['collect_count'] = get_count(collect_record_path)
	ret['compose_count'] = get_count(compose_record_path)
	return ret

if __name__ == "__main__":
	app.run(host= '0.0.0.0', port=int('80'))