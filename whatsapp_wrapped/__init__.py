from flask import Flask

app = Flask(__name__)
app.config["UPLOAD_FOLDER"] = "/secure_folder"

from whatsapp_wrapped.api.wordcloud_api import wordcloud_api
from whatsapp_wrapped.api.analytics_api import analytics_api
from whatsapp_wrapped.api.test_api import test_api

app.register_blueprint(wordcloud_api, url_prefix="/api/wordcloud")
app.register_blueprint(test_api, url_prefix="/api/test")

app.register_blueprint(analytics_api, url_prefix="/api/analytics")
from whatsapp_wrapped import routes
