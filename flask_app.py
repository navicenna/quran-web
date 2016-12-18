
# A very simple Flask Hello World app for you to get started with...

from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def hello_world():
    r = input("input")
    return 'Hello from Flask!' + r

