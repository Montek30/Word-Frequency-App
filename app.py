import requests, re
import nltk, operator
from flask import Flask, render_template, request, Response
from flask_migrate import Migrate
from bs4 import BeautifulSoup
from collections import Counter
from nltk.corpus import stopwords

app = Flask(__name__)

@app.route('/', methods=["GET","POST"])
def home():
	errors = ""
	response = {}
	url = ''
	if request.method == "POST":
		url = request.form["url"]
		res = data_process(url)
		if res == -1:
			return render_template("home.html", errors="Please enter a valid URL")
		else:
			return render_template("home.html",errors=errors, response=res, download_url=url)
	else:
		return render_template("home.html",errors=errors, response=response, download_url=url)

def data_process(url):
	try:
		url_data = requests.get(url)
	except:
		return -1 
	
	if url_data:
		data = BeautifulSoup(url_data.text, 'html.parser').get_text()
		tokens = nltk.word_tokenize(data)
		text = nltk.Text(tokens)			
		non_punctuation = re.compile('.*[A-Za-z].*')
		
		raw_words = []
		for w in text:
			if non_punctuation.match(w):
				raw_words.append(w)
		
		stop_words = set(stopwords.words('english'))
		filtered_sentence = []
		for w in raw_words:
			if w not in stop_words:
				filtered_sentence.append(w)
		raw_word_count = Counter(filtered_sentence)

		response = sorted(raw_word_count.items(), key=operator.itemgetter(1), reverse=True)

	return response


@app.route("/download")
def download():
	url = request.args.get('url')
	res = data_process(url)
	csv = "Word,Count\n"
	if res != -1:
		for i in res:
			csv += i[0]+","+str(i[1])+"\n"
	else:
		return {"error":"Invalid URL!!!!!"}
	
	return Response(csv,mimetype="text/csv",headers={"Content-disposition":"attachment; filename=word_count_file.csv"})


if __name__ == '__main__':
    app.debug = True
    app.run()