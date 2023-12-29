import io, base64
from flask import render_template, request, send_file, current_app
from whatsapp_wrapped import app


@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        file = request.files.get("file")

        if not file:
            return render_template("index.html", error="No file part")

        response = current_app.test_client().post(
            "/api/wordcloud/generate", data={"file": (file, "chat.txt")}
        )

        if response.status_code == 200:
            img_data = response.data
            img_base64 = base64.b64encode(img_data).decode("utf-8")

            return render_template("results.html", wordcloud_image=img_base64)
        else:
            return render_template("index.html", error="Error generating Word Cloud")

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
