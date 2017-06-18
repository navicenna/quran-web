# Quran web analysis code

# This Python file uses the following encoding: utf-8
# Test commit

import os, sys, re, csv

arabic2english = {
      u"\u0621": "'", # hamza-on-the-line
      u"\u0622": "|", # madda
      u"\u0623": ">", # hamza-on-'alif
      u"\u0624": "&", # hamza-on-waaw, treat as waaw for now
      u"\u0625": "<", # hamza-under-'alif
      u"\u0626": "}", # hamza-on-yaa'
      u"\u0627": "A", # bare 'alif
      u"\u0628": "b", # baa'
      u"\u0629": "h", # taa' marbuuTa, treat as haa'
      u"\u062A": "t", # taa'
      u"\u062B": "v", # thaa'
      u"\u062C": "j", # jiim
      u"\u062D": "H", # Haa'
      u"\u062E": "x", # khaa'
      u"\u062F": "d", # daal
      u"\u0630": "*", # dhaal
      u"\u0631": "r", # raa'
      u"\u0632": "z", # zaay
      u"\u0633": "s", # siin
      u"\u0634": "$", # shiin
      u"\u0635": "S", # Saad
      u"\u0636": "D", # Daad
      u"\u0637": "T", # Taa'
      u"\u0638": "Z", # Zaa' (DHaa')
      u"\u0639": "E", # cayn
      u"\u063A": "g", # ghayn
      u"\u0640": "_", # taTwiil
      u"\u0641": "f", # faa'
      u"\u0642": "q", # qaaf
      u"\u0643": "k", # kaaf
      u"\u0644": "l", # laam
      u"\u0645": "m", # miim
      u"\u0646": "n", # nuun
      u"\u0647": "h", # haa'
      u"\u0648": "w", # waaw
      u"\u0649": "y", # 'alif maqSuura, replace with yaa'
      u"\u064A": "y", # yaa'
      u"\u064B": "F", # fatHatayn
      u"\u064C": "N", # Dammatayn
      u"\u064D": "K", # kasratayn
      u"\u064E": "a", # fatHa
      u"\u064F": "u", # Damma
      u"\u0650": "i", # kasra
      u"\u0651": "~", # shaddah
      u"\u0652": "o", # sukuun
      u"\u0670": "`", # dagger 'alif
      u"\u0671": "{", # waSla
}

def transString(string, reverse=0):
    '''Given a Unicode string, transliterate into Buckwalter. To go from
    Buckwalter back to Unicode, set reverse=1'''
    silents = ["|", "&", "F", "N", "K", "a", "u", "i", "~", "o", "{"] #map these diacritical marks to empty string

    string = string.replace("|", ".")
    for k,v in arabic2english.items():
        string = string.replace(k,v)
    for letter in silents:
        string = string.replace(letter, "")

    return string

def init_tgv_dict():
      tgv_dict = {
            "'": {"tgv": 3, "gv": 0}, # hamza-on-the-line
            "|": {"tgv": 3, "gv": 0}, # madda
            ">": {"tgv": 3, "gv": 0}, # hamza-on-'alif
            "&": {"tgv": 39, "gv": 0}, # hamza-on-waaw, treat as waaw for now
            "<": {"tgv": 3, "gv": 0}, # hamza-under-'alif
            "}": {"tgv": 48, "gv": 0}, # hamza-on-yaa'
            "A": {"tgv": 3, "gv": 0}, # bare 'alif
            "b": {"tgv": 6, "gv": 0}, # baa'
            "h": {"tgv": 36, "gv": 0}, # taa' marbuuTa, treat as haa'
            "t": {"tgv": 425, "gv": 0}, # taa'
            "v": {"tgv": 527, "gv": 0}, # thaa'
            "j": {"tgv": 11, "gv": 0}, # jiim
            "H": {"tgv": 22, "gv": 0}, # Haa'
            "x": {"tgv": 631, "gv": 0}, # khaa'
            "d": {"tgv": 16, "gv": 0}, # daal
            "*": {"tgv": 944, "gv": 0}, # dhaal
            "r": {"tgv": 230, "gv": 0}, # raa'
            "z": {"tgv": 25, "gv": 0}, # zaay
            "s": {"tgv": 87, "gv": 0}, # siin
            "$": {"tgv": 334, "gv": 0}, # shiin
            "S": {"tgv": 122, "gv": 0}, # Saad
            "D": {"tgv": 841, "gv": 0}, # Daad
            "T": {"tgv": 34, "gv": 0}, # Taa'
            "Z": {"tgv": 944, "gv": 0}, # Zaa' (DHaa')
            "E": {"tgv": 104, "gv": 0}, # cayn
            "g": {"tgv": 1047, "gv": 0}, # ghayn
            "_": {"tgv": 0, "gv": 0}, # taTwiil
            "f": {"tgv": 117, "gv": 0}, # faa'
            "q": {"tgv": 140, "gv": 0}, # qaaf
            "k": {"tgv": 53, "gv": 0}, # kaaf
            "l": {"tgv": 65, "gv": 0}, # laam
            "m": {"tgv": 77, "gv": 0}, # miim
            "n": {"tgv": 89, "gv": 0}, # nuun
            "h": {"tgv": 36, "gv": 0}, # haa'
            "w": {"tgv": 39, "gv": 0}, # waaw
            "y": {"tgv": 48, "gv": 0}, # 'alif maqSuura, replace with yaa'
            "y": {"tgv": 48, "gv": 0}, # yaa'
            "F": {"tgv": 0, "gv": 0}, # fatHatayn
            "N": {"tgv": 0, "gv": 0}, # Dammatayn
            "K": {"tgv": 0, "gv": 0}, # kasratayn
            "a": {"tgv": 0, "gv": 0}, # fatHa
            "u": {"tgv": 0, "gv": 0}, # Damma
            "i": {"tgv": 0, "gv": 0}, # kasra
            "~": {"tgv": 0, "gv": 0}, # shaddah
            "o": {"tgv": 0, "gv": 0}, # sukuun
            "`": {"tgv": 3, "gv": 0}, # dagger 'alif
            "{": {"tgv": 0, "gv": 0}, # waSla
      }
      return tgv_dict

def calc_val(word, type_v):
    rv = 0

    tgv_dict = init_tgv_dict()
    for letter in word:
        try:
            rv += tgv_dict[letter][type_v]
        except:
            pass

    return  rv

# Detect Arabic language
def detect_arabic(string):
    for letter in arabic2english:
        if letter in string:
            return True
    return False