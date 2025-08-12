""" 
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope Process 
.\venv\Scripts\Activate.ps1
"""
import threading
from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from discord_bot import run 
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
    bot_thread = threading.Thread(target=run, daemon=True)
    bot_thread.start()
    app.run(use_reloader=False)
    
    
    