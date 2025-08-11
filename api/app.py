""" 
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope Process 
.\venv\Scripts\Activate.ps1
"""
import threading
from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
import os
from dotenv import load_dotenv
import sys
import os

# Add parent directory (project root) to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from discord_bot import bot

app = Flask(__name__)

load_dotenv()
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


def start_bot():
    bot.run(os.getenv("TOKEN"))


if __name__ == "__main__":
    threading.Thread(target=start_bot, daemon=True).start()
    app.run(use_reloader=False)
    
    