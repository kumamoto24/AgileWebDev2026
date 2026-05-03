from flask import send_from_directory
from app import app
import os

@app.route("/profile")
def profile():
    return send_from_directory(".", "myprofile.html")