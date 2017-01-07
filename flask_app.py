
# A very simple Flask Hello World app for you to get started with...

from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def hello_world():
    # r = input("input")
    return render_template("main_page.html")

@app.route('/wibble')
def wibble():
    return 'test'
