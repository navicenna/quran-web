
# A very simple Flask Hello World app for you to get started with...

from flask import Flask, redirect, render_template, request, url_for
import logging
import re
from flask_debugtoolbar import DebugToolbarExtension
from flask.ext.sqlalchemy import SQLAlchemy
from funcs import init_tgv_dict, calc_val, transString
from funcs_process_quran_text import verse2dict
from sqlalchemy import text

app = Flask(__name__)
app.debug = True
app.config["DEBUG"] = True
app.config["SECRET_KEY"] = 'SK119'
app.config["DEBUG_TB_INTERCEPT_REDIRECTS"] = False


toolbar = DebugToolbarExtension(app)

SQLALCHEMY_DATABASE_URI = "mysql+mysqlconnector://{username}:{password}@{hostname}/{databasename}".format(
    username="navid",
    password="triumph119",
    hostname="navid.mysql.pythonanywhere-services.com",
    databasename="navid$qdb",
)
app.config["SQLALCHEMY_DATABASE_URI"] = SQLALCHEMY_DATABASE_URI
app.config["SQLALCHEMY_POOL_RECYCLE"] = 299

db = SQLAlchemy(app)

class Word(db.Model):

    __tablename__ = "words"

    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(4096))


class Verse(db.Model):

    __tablename__ = "q_tbl"

    id = db.Column(db.Integer, primary_key=True)
    nSura = db.Column(db.Integer)
    nVerse = db.Column(db.Integer)
    verse = db.Column(db.String(4096))



# Load Quran into table. First delete it, then add rows.
n = Verse.query.delete()
db.session.commit()

quran_file = "/home/navid/mysite/quran-simple.txt"

testlines=[]
with open(quran_file, "r", encoding="utf-8") as f:
    lines = [l.strip() for l in f.readlines()]
    for x in range(10):
        testlines.append(lines[x])

test = True

if test:
    n = 111
else:
    n = 50100

for l in lines[0:n]:
    # print(l)
    temp_verse = verse2dict(l)
    # print(temp_verse)
    temp_verse = Verse(nSura=temp_verse["sura"],
                      nVerse=temp_verse["verse"],
                      verse=temp_verse["text"])

    db.session.add(temp_verse)
db.session.commit()

# testlines = Verse.query.limit(10).all()

verse_obj = []

# Main web application function
@app.route("/", methods=["GET", "POST"])
def index():
    global verse_obj

    # test=['a', 'b']
    if request.method == "GET":
        return render_template("main_page.html", comments=Word.query.all(), verses=verse_obj)
    else:
        execute_this = request.form["submit"]
        logging.error(request.form)
        if execute_this == "Clear":
            n = Word.query.delete()
            db.session.commit()
            print(n)
        elif execute_this == "Calculate TGV":
            word = request.form["contents"]
            addition = calc_val(transString(word), "tgv")
            string = "TGV of " + word + " is: " + str(addition)
            comment = Word(content=string)
            db.session.add(comment)
            db.session.commit()
        elif execute_this == "Get verse":
            req = request.form["contents"].strip()

            verse_obj = query_verses(req, db)
        return redirect(url_for('index'))



@app.route('/wibble')
def wibble():
    return 'test'





# process request to query
def query_verses(req, db):
    req = re.split("\D+", req)
    if len(req) < 3:
        req[2], req[3] = req[0], req[1]

    begSura = req[0]
    begVerse = req[1]
    endSura = req[2]
    endVerse = req[3]

    if begSura==endSura:
        textual = text("select nSura, nVerse, verse from q_tbl where nSura = :x1 and nVerse >= :x2 and nVerse <= :x4 ")
        rv = db.session.execute(textual, {"x1": begSura, "x2": begVerse, "x4": endVerse}).fetchall()
    else:
        textual = text("select nSura, nVerse, verse from q_tbl where (nSura = :x1 and nVerse >= :x2)" +
        " or (nSura > :x1 and nSura < :x3) or (nSura = :x3 and nVerse <= :x4")
        rv = db.session.execute(textual, {"x1": begSura, "x2": begVerse, "x3": endSura, "x4": endVerse}).fetchall()

    return load_query_into_dict(rv)


def load_query_into_dict(queried_verses):
    rv = []
    d = {}

    for v in queried_verses:
        di = d.copy()
        di["nSura"] = v[0]
        di["nVerse"] = v[1]
        di["text"] = v[2]
        rv.append(di.copy())

    return rv


# def search_word()









