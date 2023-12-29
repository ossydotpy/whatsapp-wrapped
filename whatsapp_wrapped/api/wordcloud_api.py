import re, io
from flask import Blueprint, jsonify, request, send_file
from wordcloud import WordCloud, STOPWORDS

wordcloud_api = Blueprint("wordcloud_api", __name__)


@wordcloud_api.route("/generate", methods=["POST"])
def generate_wordcloud():
    file = request.files.get("file")

    if not file:
        return jsonify({"error": "No file part"}), 400

    data = file.read().decode("utf-8").splitlines()

    cleaned = []
    words = []

    for line in data:
        if "<Media omitted>" not in line and not re.search(r"https?://\S+", line):
            cleaned_line = line.strip("\n")
            cleaned.append(cleaned_line)

            messages = re.findall(
                r"\d+/\d+/\d+, \d+:\d+\s*PM - (.*?): (.*?)$", cleaned_line
            )

            for message in messages:
                words.extend(message[1].split())

    text = " ".join(words)

    stopwords = set(STOPWORDS)
    stopwords.update(
        ["the", "and", "is", "on", "for", "a", "in", "be", "so", "can", "if", "u", "go"]
    )

    wordcloud = WordCloud(
        stopwords=stopwords, width=600, height=1200, max_words=100
    ).generate(text)

    img_buffer = io.BytesIO()
    wordcloud.to_image().save(img_buffer, format="PNG")
    img_buffer.seek(0)

    return send_file(img_buffer, mimetype="image/png")
