#!/usr/bin/python3.6
# A very simple Flask Hello World app for you to get started with...

from flask import Flask, redirect, render_template, request, url_for, Markup
from flask_sslify import SSLify
import logging
import re
from flask_debugtoolbar import DebugToolbarExtension
from flask.ext.sqlalchemy import SQLAlchemy
from funcs import init_tgv_dict, calc_val, transString, detect_arabic, remove_diacritics
from funcs_process_quran_text import *
from sqlalchemy import text
from collections import OrderedDict
import solver


app = Flask(__name__)
sslify = SSLify(app)
app.debug = True
app.config["DEBUG"] = True
app.config["SECRET_KEY"] = 'SK119'
app.config["DEBUG_TB_INTERCEPT_REDIRECTS"] = False


# toolbar = DebugToolbarExtension(app)

SQLALCHEMY_DATABASE_URI = "mysql+mysqlconnector://{username}:{password}@{hostname}/{databasename}".format(
    username="navid",
    password="triumph119",
    hostname="navid.mysql.pythonanywhere-services.com",
    databasename="navid$qdb",
)
app.config["SQLALCHEMY_DATABASE_URI"] = SQLALCHEMY_DATABASE_URI
app.config["SQLALCHEMY_POOL_RECYCLE"] = 299
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

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
    seq_order = db.Column(db.Integer)
    chron_order = db.Column(db.Integer)

# Variables to determine whether the raw Quran input should be loaded upon running
#   the script, and if it should be loaded, just a test portion or the whole Quran
quran_load = False
quran_test = False

# Load Quran into table. First delete it, then add rows.
quran_file = "/home/navid/mysite/eng_quran_out.txt"
sura_order_table = "/home/navid/mysite/sura_order.csv"
if quran_load:
    n = Verse.query.delete()
    db.session.commit()

    qdf = solver.quran_as_df(quran_file, sura_order_table)

    if quran_test:  # if testing mode, only work with first few rows of data
        n = 111
    else:
        n = 50100

    i = 0
    for verse in qdf[0:n].itertuples():
        temp_verse = Verse(nSura=verse.sura,
                           nVerse=verse.verse,
                           ar=verse.arabic,
                           eng=verse.english,
                           translit=transString(verse.arabic),
                           seq_order=verse.seq_index,
                           chron_order=verse.chron_index
                          )
        db.session.add(temp_verse)
        i+=1
    db.session.commit()

# Build Quran dictionary and TGV dictionary
quran_dict = scrape_quran_into_dict(quran_file)
print("assembled quran_dict")
all_ngrams = get_ngrams_quran(quran_dict)
print("assembled ngrams phase 1...")
ngrams_sub = all_ngrams[0:6]

#tgv_dict = build_tgv_dict(ngrams_sub)



# Store queried verses
verse_obj, verse_obj_ordered = [], []
# Store alif count
alif_count = "N/A"
# Store search word(s)
search_term = 'N/A'
search_term_ordered = 'N/A'
# other vars
result = ""


# Main web application function
@app.route("/", methods=["GET", "POST"])
def index():
    global verse_obj, alif_count, search_term
    alif_count = ""

    # test=['a', 'b']
    if request.method == "GET":
        # search_term = '_undefined_' if len(search_term) < 1 else search_term
        return render_template("main_page.html", comments=Word.query.all(), verses=verse_obj,
                                 alif_count=alif_count, search_term=search_term)
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
                verse_obj_pre = query_verses_number(req, db)
                search_term = 'N/A'
            else:
                search_term = remove_diacritics(req) if detect_arabic(req) else req
                verse_obj_pre = query_verses_text(req, db)
            verse_obj = []
            for verse_dict in verse_obj_pre:
                temp = verse_dict.copy()
                temp['ar'] = remove_diacritics(verse_dict['ar'])
                verse_obj.append(temp)

        return redirect(url_for('index'))


# Ordered search function
@app.route("/ordered_verse_search", methods=["GET", "POST"])
def ordered_verse_search():
    global verse_obj_ordered, search_term_ordered
    alif_count = ""

    # test=['a', 'b']
    if request.method == "GET":
        # search_term_ordered = '_undefined_' if len(search_term_ordered) < 1 else search_term_ordered
        return render_template("ordered_verse_search.html", comments=Word.query.all(), verses=verse_obj_ordered,
                                 alif_count=alif_count, search_term=search_term_ordered)
    else:
        execute_this = request.form["submit"]
        logging.error(request.form)
        if execute_this == "Get verse":
            req = request.form["contents"].strip()
            # order_selection = request.form["order-type"].strip()
            if re.match(r"\d+.*",req):
                verse_obj_pre = query_verses_order(req, db, "na")

            # Remove diacritics from Arabic text
            verse_obj_ordered = []
            for verse_dict in verse_obj_pre:
                temp = verse_dict.copy()
                temp['ar'] = remove_diacritics(verse_dict['ar'])
                verse_obj_ordered.append(temp)

        return redirect(url_for('ordered_verse_search'))


# Ordered search function
@app.route("/analysis", methods=["GET", "POST"])
def analysis():
    if request.method == "GET":
        return render_template("analysis.html")
    else:
        return redirect(url_for('analysis'))



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
        suras_selected = request.form.getlist('sura')
        suras_selected = [int(x) for x in suras_selected]
        print(suras_selected)
        sura_values = alif_count_quran(quran_dict, letters_selected, suras_selected)
        letter_count = sura_values["count"]
        tgv = sura_values["tgv"]
        result = Markup("Count of selected letters in selected suras: " + str(letter_count) +
                    "<br>Total TGV of selected letters in selected suras: " + str(tgv))
        return redirect(url_for('dashboard'))
    else:
        return render_template("dashboard.html", letters=fetch_trans_dict(),
                                result=result, sura_numbers=fetch_sura_numbers())



# TGV matching app
@app.route("/tgv_matching", methods=["GET", "POST"])
def tgv_matching():
    global verse_obj, alif_count
    alif_count=""

    # test=['a', 'b']
    if request.method == "GET":
        return render_template("tgv_matching.html", comments=Word.query.all(), verses=verse_obj,
                                 alif_count=alif_count, search_package={})
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
        elif execute_this == "Find TGV pairs":
            req = request.form["contents"].strip()
            if re.fullmatch('\d*', req):
                tgv = int(req)
                pairs = [ngram for ngram in all_ngrams if ngram['tgv'] == tgv]
                pairs_dict = build_tgv_match_dict(pairs)
                search_package = {'term': tgv, 'type': 'number'}
            else:
                word = req
                tgv = calc_val(transString(word), "tgv")
                pairs = [ngram for ngram in all_ngrams if ngram['tgv'] == tgv]
                pairs_dict = build_tgv_match_dict(pairs)
                search_package = {'term': word, 'type': 'word'}
            return render_template("tgv_matching.html", comments=Word.query.all(),
                                    pairs=pairs_dict, search_package=search_package, tgv=tgv)
        return redirect(url_for('tgv_matching'))



# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#       HELPER FUNCTIONS
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


def concat_sura_verse(sura, verse):
    '''Given sura and verse number, return a string like so: "2:30"'''
    sura = str(sura)
    verse = str(verse)
    return sura + ":" + verse


def build_tgv_match_dict(ngrams):
    ''' '''
    rv = {}
    for ngram_dict in ngrams:
        gram = remove_diacritics(ngram_dict['gram'])
        if gram in rv.keys():
            rv[gram].append(concat_sura_verse(ngram_dict['sura_nbr'], ngram_dict['verse_nbr']))
        else:
            rv[gram] = [concat_sura_verse(ngram_dict['sura_nbr'], ngram_dict['verse_nbr'])]
    for gram in rv:
        rv[gram] = ", ".join(rv[gram])
    # rv2 = OrderedDict(rv)
    rv = OrderedDict(sorted(rv.items(), key=lambda t: t[0]))
    return rv


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
        textual = text(
            "select nSura, nVerse, ar, eng, seq_order, chron_order from q_tbl where nSura = :x1 and nVerse >= :x2 and nVerse <= :x4 ")
        rv = db.session.execute(textual, {"x1": begSura, "x2": begVerse, "x4": endVerse}).fetchall()
    else:
        textual = text("select nSura, nVerse, ar, eng, seq_order, chron_order from q_tbl where (nSura = :x1 and nVerse >= :x2)" +
        " or (nSura > :x1 and nSura < :x3) or (nSura = :x3 and nVerse <= :x4)")
        rv = db.session.execute(textual, {"x1": begSura, "x2": begVerse, "x3": endSura, "x4": endVerse}).fetchall()

    return load_query_into_dict(rv)


# process request to query certain verses by order
def query_verses_order(req, db, order_type):
    req = re.split("\D+", req)
    print(req)

    order = req[0]
    order_type = "Chronological"
    # order_field = "seq_order" if order_type=="Sequential" else "chron_order"
    # query = "select nSura, nVerse, ar, eng, seq_order, chron_order from q_tbl where {} = :x1".format(order_field)
    query = "select nSura, nVerse, ar, eng, seq_order, chron_order from q_tbl where seq_order = :x1 or chron_order = :x1"
    textual = text(query)
    rv = db.session.execute(textual, {"x1": order}).fetchall()

    return load_query_into_dict(rv)


# process request to run word search on verses
def query_verses_text(req, db):
    if req=="":
        return [{}]
    req=req.strip()

    if detect_arabic(req):
        search = '%' + transString(req) + '%'
        textual = text("select nSura, nVerse, ar, eng, seq_order, chron_order from q_tbl " +
                       "where translit like :x1")
    else:
        search = '%' + req + '%'
        textual = text("select nSura, nVerse, ar, eng, seq_order, chron_order from q_tbl " +
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
            di["seq_order"] = v[4]
            di["chron_order"] = v[5]
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



