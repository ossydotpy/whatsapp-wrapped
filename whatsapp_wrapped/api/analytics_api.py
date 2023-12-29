from flask import Blueprint, request, jsonify

from whatsapp_wrapped.utils import make_df, preprocess_chat, \
get_sentiment_percentages, get_top_initiator, get_message_count_stats

analytics_api = Blueprint("analytics_api", __name__)

time_ranges = {
    "morning": "6:00am - 11:59am",
    "afternoon": "12:00pm - 4:00pm",
    "evening": "4:01pm - 8:59pm",
    "night": "9:00pm - 3:00am",
    "dawn": "3:01am - 5:59am",
}

@analytics_api.route("/chat_analysis", methods=["POST"])
def get_analysis():
    try:
        file = request.files.get("file")

        if not file:
            return jsonify({"error": "No file part"}), 400

        # preprocess and make df
        cleaned_file_data = preprocess_chat(file)
        df = make_df(cleaned_file_data)

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
        return jsonify(chat_stats)

    except Exception as e:
        return jsonify({"error": str(e)}), 500