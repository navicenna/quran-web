
# A very simple Flask Hello World app for you to get started with...

from flask import Flask, redirect, render_template, request, url_for, Markup
import logging
import re
from flask_debugtoolbar import DebugToolbarExtension
from flask.ext.sqlalchemy import SQLAlchemy
from funcs import init_tgv_dict, calc_val, transString, detect_arabic
from funcs_process_quran_text import *
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
    ar = db.Column(db.String(4096))
    eng = db.Column(db.String(4096))
    translit = db.Column(db.String(4096)) #English transliteration

# Variables to determine whether the raw Quran input should be loaded upon running
#   the script, and if it should be loaded, just a test portion or the whole Quran
quran_load = True
quran_test = False

# Load Quran into table. First delete it, then add rows.
quran_file = "/home/navid/mysite/eng_quran_out.txt"
if quran_load:
    n = Verse.query.delete()
    db.session.commit()

    testlines=[]
    with open(quran_file, "r", encoding="utf-8") as f:
        lines = [l.strip() for l in f.readlines()]
        for x in range(10):
            testlines.append(lines[x])



    if quran_test:
        n = 111
    else:
        n = 50100

    for l in lines[0:n]:
        # print(l)
        temp_verse = verse2dict(l)
        # print(temp_verse)
        temp_verse = Verse(nSura=temp_verse["nSura"],
                          nVerse=temp_verse["nVerse"],
                          ar=temp_verse["ar"],
                          eng=temp_verse["eng"],
                          translit=temp_verse["translit"]
                          )

        db.session.add(temp_verse)
    db.session.commit()

# Quran dictionary
quran_dict = scrape_quran_into_dict(quran_file)

# Store queried verses
verse_obj = []
# Store alif count
alif_count = "N/A"
# other vars
result = ""


# Main web application function
@app.route("/", methods=["GET", "POST"])
def index():
    global verse_obj, alif_count

    # test=['a', 'b']
    if request.method == "GET":
        return render_template("main_page.html", comments=Word.query.all(), verses=verse_obj,
                                 alif_count=alif_count)
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

        elif execute_this == "Count alif":
            req = request.form["contents"].strip()
            req = list( map( int, re.split("\D+", req) ))

            if len(req) == 1:
                sura = req[0]
                alif_count = alif_count_sura(quran_dict, sura, ["A"])
            else:
                try:
                    sura, verse = req[0], req[1]
                    alif_count = alif_count_verse(quran_dict, sura, verse, ["A"])
                except:
                    alif_count = "Invalid sura-verse input"


        elif execute_this == "Get verse":
            req = request.form["contents"].strip()
            if re.match("\d+\D+\d+\D*",req):
                verse_obj = query_verses_number(req, db)
            else:
                verse_obj = query_verses_text(req, db)
        return redirect(url_for('index'))



# @app.route('/wibble')
# def wibble():
#     return 'test'


@app.route('/example_arabic_lesson')
def example_arabic_lesson():
    return render_template("example_arabic_lesson.html")

# Letter count dashboard
@app.route('/dashboard', methods=["GET", "POST"])
def dashboard():
    global result

    # result = "test result"
    if request.method == "POST":
        letters_selected = request.form.getlist('letter')
        print(letters_selected)
        sura_values = alif_count_quran(quran_dict, letters_selected)
        letter_count = sura_values["count"]
        tgv = sura_values["tgv"]
        result = Markup("Count of selected letters in Quran: " + str(letter_count) +
                    "<br>Total TGV of selected letters in Quran: " + str(tgv))
        return redirect(url_for('dashboard'))
    else:
        return render_template("dashboard.html", letters=fetch_trans_dict(), result=result)






# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#       HELPER FUNCTIONS
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~



# process request to query certain verse numbers
def query_verses_number(req, db):
    req = re.split("\D+", req)
    print(req)
    if len(req) < 3:
        req.extend( [ req[0], req[1] ] )

    begSura = req[0]
    begVerse = req[1]
    endSura = req[2]
    endVerse = req[3]

    if begSura==endSura:
        textual = text("select nSura, nVerse, ar, eng from q_tbl where nSura = :x1 and nVerse >= :x2 and nVerse <= :x4 ")
        rv = db.session.execute(textual, {"x1": begSura, "x2": begVerse, "x4": endVerse}).fetchall()
    else:
        textual = text("select nSura, nVerse, ar, eng from q_tbl where (nSura = :x1 and nVerse >= :x2)" +
        " or (nSura > :x1 and nSura < :x3) or (nSura = :x3 and nVerse <= :x4)")
        rv = db.session.execute(textual, {"x1": begSura, "x2": begVerse, "x3": endSura, "x4": endVerse}).fetchall()

    return load_query_into_dict(rv)


# process request to run word search on verses
def query_verses_text(req, db):
    if req=="":
        return [{}]
    req=req.strip()

    if detect_arabic(req):
        search = '%' + transString(req) + '%'
        textual = text("select nSura, nVerse, ar, eng, translit from q_tbl " +
                       "where translit like :x1")
    else:
        search = '%' + req + '%'
        textual = text("select nSura, nVerse, ar, eng, translit from q_tbl " +
                       "where eng like :x1")

    print("req is: ", req)
    print("search is: ", search)
    rv = db.session.execute(textual, {"x1": search}).fetchall()

    return load_query_into_dict(rv)



# Load query result into a dictionary for easy processing by flask HTML processor
def load_query_into_dict(queried_verses):
    rv = []
    d = {}

    for v in queried_verses:
        di = d.copy()
        di["nSura"] = v[0]
        di["nVerse"] = v[1]
        di["ar"] = v[2]
        di["eng"] = v[3]
        try:
            di["translit"] = v[4]
        except:
            pass
        rv.append(di.copy())
    return rv



# Count number of letters in a verse; based on English transliteration
def count_letter(verse, letter):
    only_letters = [l for l in verse if l==letter]
    return len(only_letters)



if __name__ == "main":
    app.debug = True



