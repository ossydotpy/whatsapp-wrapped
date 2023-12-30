import io, base64, json
from .utils import edit_count_image, edit_top_initiator, edit_active_hours, edit_sentiment_analysis, edit_individual_count_image
from flask import render_template, request, send_file, current_app
from whatsapp_wrapped import app


@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        file = request.files.get("file")

        if not file:
            return render_template("index.html", error="No file part")

        response = current_app.test_client().post(
            "/api/analytics/chat_analysis", data={"file": (file, "chat.txt")}
        )

        if response.status_code == 200:
            json_data = json.loads(response.data)
            chat_count = edit_count_image(json_data)
            top_initiator = edit_top_initiator(json_data)
            peak_hours = edit_active_hours(json_data)
            sentiments = edit_sentiment_analysis(json_data)
            individual_stats = edit_individual_count_image(json_data)

            chat_count_base64 = base64.b64encode(chat_count.getvalue()).decode("ascii")
            top_initiator_base64 = base64.b64encode(top_initiator.getvalue()).decode("ascii")
            peak_hours_base64 = base64.b64encode(peak_hours.getvalue()).decode("ascii")
            sentiments_base64 = base64.b64encode(sentiments.getvalue()).decode("ascii")
            individual_stats_base64 = base64.b64encode(individual_stats.getvalue()).decode("ascii")

            return render_template("results.html", chat_count_img=chat_count_base64,\
                                   top_ini = top_initiator_base64, peak_img = peak_hours_base64,\
                                    sentiments_img =sentiments_base64, individual_img=individual_stats_base64)
        else:
            return render_template("index.html", error="Error generating some images")

    return render_template("index.html")



@app.route("/download_wordcloud")
def download_wordcloud():
    response = current_app.test_client().post(
        "/api/wordcloud/generate", data={"file": ("dummy content", "dummy.txt")}
    )

    if response.status_code == 200:
        filename = "wordcloud.png"
        img_data = response.data

        return send_file(
            io.BytesIO(img_data),
            mimetype="image/png",
            as_attachment=True,
            download_name=filename,
        )
    else:
        return render_template("index.html", error="Error generating Word Cloud")
