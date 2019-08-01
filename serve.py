from flask import Flask, request, send_from_directory, render_template

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
def handle_data():
    query_str = request.form['query']
    import subprocess
	return subprocess.check_output(['/home/ubuntu/galago-3.16-bin/bin/galago', 'batch-search', '--index=/tmp/hackathon-podcast-search.idx', '--passageQuery=true', '--passageSize=50', '--passageShift=25', '--queryType=simple', '--requested=10', "--query='"+query_str+"'"])

if __name__ == "__main__":
    app.run()