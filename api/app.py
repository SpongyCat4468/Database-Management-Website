import threading
from flask import Flask, render_template
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from discord_bot import run  # your bot's run() function

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
    return render_template("index.html", commands=commands_text)


if __name__ == "__main__":
    # Start Discord bot in background
    bot_thread = threading.Thread(target=run)
    bot_thread.start()

    # Start Flask server (Render will set PORT environment variable)
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, use_reloader=False, threaded=True)

