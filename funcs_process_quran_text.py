# This Python file uses the following encoding: utf-8

import re



# A dictionary that maps every possible Arabic letter to an English transliteration
arabic2english = {
      u"\u0621": "'", # hamza-on-the-line
      u"\u0622": "|", # madda
      u"\u0623": "A", # hamza-on-'alif
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



def transString(string):
    '''Given a Unicode string, transliterate into Buckwalter'''

    silents = ["|", "&", "F", "N", "K", "a", "u", "i", "~", "o", "{"] #map these diacritical marks to empty string

    # string = string.replace("|", ".")
    for k,v in arabic2english.items():
        string = string.replace(k,v)
    for letter in silents:
        string = string.replace(letter, "")

    return string



def verse2dict(verse):
    '''function used to read in Arabic Quran text. Use regular expression
    pattern matching to extract sura and verse number, and Arabic and English text
    from Quran text file'''

    rd = {}
    rd["nSura"] = re.search("\d{1,3}\|", verse).group(0)[0:-1]
    rd["nVerse"] = re.search("\|\d{1,3}\|", verse).group(0)[1:-1]
    rd["ar"] = verse.split("|")[2]
    rd["eng"] = verse.split("|")[3]
    rd["translit"] = transString(rd["ar"])

    return rd



# The following code is not used. Delete after confirming (Navid - 5/4/2017 05:22:33)
# def vdict2list(vdict):
#     ''''''
#     rl=[]
#     for letter in vdict["text"]:
#         if letter != ' ':
#             # print(letter)
#             temp = vdict
#             temp["letter"] = letter
#             # print(temp)
#             rl.append(vdict.copy())
#     return rl

# def quran2csvlines(quran):
#     rl = []
#     for line in quran:
#         rl.extend(vdict2list(verse2dict(line)))
#     return rl


# Given a Quran dictionary and a verse, add the verse into the dictionary
def scrape_verse(quran_dict, verse):
  sura, verse, arabic, english = verse.split("|")
  # try:
  sura, verse = int(sura), int(verse)
  # except:
  #   print(sura, verse)

  if sura not in quran_dict.keys():
    quran_dict[sura] = {}

  quran_dict[sura][verse] = {}
  quran_dict[sura][verse]["arabic"] = arabic
  quran_dict[sura][verse]["english"] = english

  return


# Open the text file of Quran and scrape it into a nested dictionary
# data structure
# 
# Returns: dictionary
def scrape_quran_into_dict(quran_file):
  with open(quran_file, "r", encoding="utf-8") as f:
    lines = f.readlines()

    rv = {}
    for l in lines[0:4]:
      scrape_verse(rv, l)

    return rv


# TESTING
f = "eng_quran_out.txt"
d = scrape_quran_into_dict(f)
print(d)
# 