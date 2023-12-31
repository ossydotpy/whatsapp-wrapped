import io, base64, json
from .utils import edit_count_image, edit_top_initiator, edit_active_hours, edit_sentiment_analysis, edit_individual_count_image
from flask import render_template, request, send_file, current_app
from whatsapp_wrapped import app


@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        file = request.files.get("file")
        file_copy = io.BytesIO(file.getvalue()) 

        if not file:
            return render_template("index.html", error="No file part")

        try:
            wordcloud_response = current_app.test_client().post(
                "/api/wordcloud/generate", data={"file": (file, "chat.txt")}
            )

            analytics_response = current_app.test_client().post(
                "/api/analytics/chat_analysis", data={"file": (file_copy, "chat.txt")}
            )

            if wordcloud_response.status_code != 200 or analytics_response.status_code != 200:
                raise Exception("API request failed")

            img_base64 = base64.b64encode(wordcloud_response.data).decode('utf-8')
            json_data = json.loads(analytics_response.data)

            chat_count_base64 = base64.b64encode(edit_count_image(json_data).getvalue()).decode("ascii")
            top_initiator_base64 = base64.b64encode(edit_top_initiator(json_data).getvalue()).decode("ascii")
            peak_hours_base64 = base64.b64encode(edit_active_hours(json_data).getvalue()).decode("ascii")
            sentiments_base64 = base64.b64encode(edit_sentiment_analysis(json_data).getvalue()).decode("ascii")
            individual_stats_base64 = base64.b64encode(edit_individual_count_image(json_data).getvalue()).decode("ascii")

            return render_template("results.html", chat_count_img=chat_count_base64,
                                   top_ini=top_initiator_base64, peak_img=peak_hours_base64,
                                   sentiments_img=sentiments_base64, individual_img=individual_stats_base64,
                                   wordcloud=img_base64)

        except Exception as e:
            app.logger.error(f"Error in processing: {e}")
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
