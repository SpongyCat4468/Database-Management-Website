""" 
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope Process 
.\venv\Scripts\Activate.ps1
"""
import threading
from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy


app = Flask(__name__)


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
    app.run(use_reloader=False)
    
    