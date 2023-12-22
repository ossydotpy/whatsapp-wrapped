from flask import Flask, render_template, request, send_file
import re
from os import path
import numpy as np
import matplotlib.pyplot as plt
from PIL import Image
from wordcloud import WordCloud, STOPWORDS

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        if 'file' not in request.files:
            return render_template('index.html', error="No file part")

        file = request.files['file']

        if file.filename == '':
            return render_template('index.html', error="No selected file")

        if file:
            data = file.read().decode('utf-8').splitlines()

            cleaned = []
            words = []

            for line in data:
                if '<Media omitted>' not in line and not re.search(r'https?://\S+', line):
                    cleaned_line = line.strip('\n')
                    cleaned.append(cleaned_line)

                    messages = re.findall(r"\d+/\d+/\d+, \d+:\d+\s*PM - (.*?): (.*?)$", cleaned_line)

                    for message in messages:
                        words.extend(message[1].split())

            text = ' '.join(words)

            stopwords = set(STOPWORDS)
            stopwords.update(['the', 'and', 'is', 'on', 'for', 'a', 'in', 'be', 'so', 'can', 'if', 'u', 'go'])

            wordcloud = WordCloud(stopwords=stopwords, width=600, height=1200, max_words=100).generate(text)

            wordcloud.to_file('static/wordcloud.png')

            return render_template('results.html')

    return render_template('index.html')

@app.route('/download_wordcloud')
def download_wordcloud():
    return send_file('static/wordcloud.png', as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)
