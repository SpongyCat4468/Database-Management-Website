import threading
import asyncio
from flask import jsonify
from flask import Flask, render_template
import os
import sys
import nest_asyncio
nest_asyncio.apply()

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from discord_bot import isOnline # import bot instance
from discord_bot import run as run_bot  # your bot run function

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

def run_flask():
    port = int(os.environ.get("PORT", 5000))
    # Use threaded=True so Flask server runs in its own threads
    app.run(host="0.0.0.0", port=port, threaded=True, use_reloader=False)

@app.route("/bot_status")
def bot_status():
    return jsonify({"online": isOnline})

async def main():
    # Start Flask in a separate thread
    flask_thread = threading.Thread(target=run_flask, daemon=True)
    flask_thread.start()
    await run_bot()

if __name__ == "__main__":
    # Run the async main() function in asyncio event loop
    asyncio.run(main())
