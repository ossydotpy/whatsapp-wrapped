import base64
import re, io
from flask import Flask, Blueprint, jsonify, request, send_file
from wordcloud import WordCloud, STOPWORDS

from whatsapp_wrapped.utils import make_df, preprocess_chat, \
    get_sentiment_percentages, get_top_initiator, get_message_count_stats


test_api = Blueprint("test_api", __name__)

time_ranges = {
    "morning": "6:00am - 11:59am",
    "afternoon": "12:00pm - 4:00pm",
    "evening": "4:01pm - 8:59pm",
    "night": "9:00pm - 3:00am",
    "dawn": "3:01am - 5:59am",
}

@test_api.route("/generate_and_analyze", methods=["POST"])
def generate_and_analyze():
    try:
        file = request.files.get("file")

        if not file:
            return jsonify({"error": "No file part"}), 400

        # Preprocess and make df
        cleaned_file_data = preprocess_chat(file)
        df = make_df(cleaned_file_data)

        # Generate Word Cloud
        words = []
        for line in cleaned_file_data:
            messages = re.findall(r"\d+/\d+/\d+, \d+:\d+\s*PM - (.*?): (.*?)$", line)
            for message in messages:
                words.extend(message[1].split())

        text = " ".join(words)
        stopwords = set(STOPWORDS)
        stopwords.update(["the", "and", "is", "on", "for", "a", "in", "be", "so", "can", "if", "u", "go"])
        wordcloud = WordCloud(stopwords=stopwords, width=600, height=1200, max_words=100).generate(text)

        # Convert Word Cloud image to base64
        img_buffer = io.BytesIO()
        wordcloud.to_image().save(img_buffer, format="PNG")
        img_base64 = base64.b64encode(img_buffer.getvalue()).decode("utf-8")

        # Analyze Chat
        timeofday = (lambda df: df["Time Range"].mode().tolist())(df)

        chat_stats = {
            "message_count": len(df),
            'message_count_by_sender': get_message_count_stats(df),
            "peak_active_hours": {
                "peak_time": timeofday[0],
                "time_range": time_ranges[timeofday[0]],
            },
            "number_of_chat_initiations": get_top_initiator(df),
            "sender_sentiment_percentage": get_sentiment_percentages(df),
        }

        # Return both Word Cloud and Chat Analysis as JSON
        return jsonify({"wordcloud": img_base64, "chat_analysis": chat_stats})

    except Exception as e:
        return jsonify({"error": str(e)}), 500
