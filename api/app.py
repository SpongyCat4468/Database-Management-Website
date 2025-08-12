from flask import Flask, render_template
import os
from flask import jsonify

app = Flask(
    __name__,
    template_folder=os.path.join(os.path.dirname(__file__), "..", "templates"),
    static_folder=os.path.join(os.path.dirname(__file__), "..", "static")
)

commands_text = """
/calc
/create_thread <channel> <name> <content>
/delete_thread <channel> <name>
/edit_thread <channel> <old_title> <new_title>
/list_thread <channel>
/random_thread <channel>
/search_thread <channel> <name>
/trend <channel>
"""

@app.route("/")
def index():
    return render_template("index.html", commands=commands_text, bot_online=True)

@app.route("/bot_status")
def bot_status():
    return jsonify({"online": True})


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)


