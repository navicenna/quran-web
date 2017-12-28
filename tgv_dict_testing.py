d = {}
d[1] = {}
d[2] = {}

d[1][1] = {"ar": "بِسْمِ اللَّهِ الرَّحْمَنِ الرَّحِيمِ"}
d[1][2] = {"ar": "الْحَمْدُ لِلَّهِ رَبِّ الْعَالَمِينَ"}
d[1][3] = {"ar": "الرَّحْمَنِ الرَّحِيمِ"}
d[1][4] = {"ar": "مَالِكِ يَوْمِ الدِّينِ"}
d[1][5] = {"ar": "إِيَّاكَ نَعْبُدُ وَإِيَّاكَ نَسْتَعِينُ"}
d[1][6] = {"ar": "اهْدِنَا الصِّرَاطَ الْمُسْتَقِيمَ"}
d[1][7] = {"ar": "صِرَاطَ الَّذِينَ أَنْعَمْتَ عَلَيْهِمْ غَيْرِ الْمَغْضُوبِ عَلَيْهِمْ وَلَا الضَّالِّينَ"}

d[2][1] = {"ar": "بِسْمِ اللَّهِ الرَّحْمَنِ الرَّحِيمِ الم"}
d[2][2] = {"ar": "ذَلِكَ الْكِتَابُ لَا رَيْبَ فِيهِ هُدًى لِلْمُتَّقِينَ"}
d[2][3] = {"ar": "الَّذِينَ يُؤْمِنُونَ بِالْغَيْبِ وَيُقِيمُونَ الصَّلَاةَ وَمِمَّا رَزَقْنَاهُمْ يُنْفِقُونَ"}

from pprint import pprint
import nltk

# pprint(d)

import nltk


def tgv(gram):
    return len(gram)


def get_ngrams_verse(sura_nbr, verse_nbr, verse):
    words = nltk.word_tokenize(verse)
    my_bigrams = [' '.join(x) for x in nltk.bigrams(words)]
    my_trigrams = [' '.join(x) for x in nltk.trigrams(words)]
    all_grams = words + my_bigrams + my_trigrams
    return [{"gram": w, "tgv": tgv(w), "sura_nbr": sura_nbr, "verse_nbr": verse_nbr}
            for w in all_grams]


def get_ngrams_sura(sura_nbr, sura):
    all_words = []
    for verse_nbr in sura:
        all_words.extend(get_ngrams_verse(
            sura_nbr, verse_nbr, sura[verse_nbr]["ar"]))
    return all_words


def get_ngrams_quran():
    all_words = []
    for sura_nbr in d:
        all_words.extend(get_ngrams_sura(sura_nbr, d[sura_nbr]))
    return list(sorted(all_words, key=lambda x: x["gram"]))


def build_tgv_dict(all_words):
    tgv_dict = {}
    max_value = max(all_words, key=lambda x: x['tgv'])['tgv']
    for i in range(1, max_value+1):
        tgv_dict[i] = [x for x in all_words if x['tgv'] is i]

    for tgv_key in list(tgv_dict):
        if len(tgv_dict[tgv_key]) == 0 :
            del tgv_dict[tgv_key]
        else:
            for gram in tgv_dict[tgv_key]:
                del gram['tgv']

    return tgv_dict


# test = get_ngrams_verse(d[1][1]["ar"])
# test = get_ngrams_sura(1, d[1])
test = get_ngrams_quran()
test_next = build_tgv_dict(test)

pprint(test_next)
# pprint(type(test))
# x = sorted(test, key=lambda x: x['tgv'])
