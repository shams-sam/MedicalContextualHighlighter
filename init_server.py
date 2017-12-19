import gensim
WORD2VEC_MODEL = '/data/Discharge_Summary/Diagnosis_ICD/master/wikipedia-pubmed-and-PMC-w2v.bin'
print("loading word2vec ...")
w2v_model = gensim.models.KeyedVectors.load_word2vec_format(WORD2VEC_MODEL, binary=True)

from Highlighter_Unigram import Highlighter_Unigram
from Highlighter_Bigram import Highlighter_Bigram
from icd_wrapper import icd_wrapper
bigram = Highlighter_Bigram()
bigram.init(w2v_model)
unigram = Highlighter_Unigram()
unigram.init(w2v_model)
coder = icd_wrapper()
coder.init()

import sys
sys.path.append('/data/Discharge_Summary/Diagnosis_ICD/src/')
sys.path.append('/data/Discharge_Summary/Diagnosis_ICD/app/')
sys.path.append('/data/Discharge_Summary/Diagnosis_ICD/logic-lab/TextPreprocessing/')
from QMap import QMap
import Config as conf
from PrefName import PrefName
import AppConfig as config
from __preprocessing import _text_preprocessing
from functools import partial
qmap = QMap(conf.ICD_SEMANTIC_TYPES)
pref_name = PrefName()
pre = partial(_text_preprocessing, remove_stopwords=True, HYPHEN_HANDLE=2)

import os
import pandas as pd
filter_files = os.listdir(config.DISCHARGE_SUMMARY_FILTER_FILES_DIR)
qmap_filters = {v: True
                for k in filter_files
                for v in pd.DataFrame.from_csv(
                    config.DISCHARGE_SUMMARY_FILTER_FILES_DIR +
                    "/" + k, header=None, index_col=None)[0].tolist()}
def qmap_bagged_concepts(sentence, result, PREFERRED=True):
    concepts = qmap.parse(sentence)
    for key, concepts_list in concepts.items():
        l = result.get(key, [])
        for concept in concepts_list:
            if concept['payload'] == None or \
                    len(concept['word'].strip()) == 0 or \
                    qmap_filters.get(concept['word'].strip().lower(), False):
                continue
            for each in concept['payload']:
                if PREFERRED and not qmap_filters.get(pref_name.get(each['cui']).strip().lower(), False):
                    l.append(pref_name.get(each['cui']).lower())
                else:
                    l.append(each['term'].lower())
        result[key] = list(set(l))
    return result

from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
app = Flask(__name__)
app.url_map.strict_slashes = False
app.config.update(
    DEBUG=False
)
CORS(app)

@app.route("/flask_status", methods=['GET'])
def flask_status():
    return "Flask server is running..."

@app.route("/get_info", methods=['GET'])
def get_info():
    sentence = request.args.get('q')
    print(sentence)
    bigram_seq, bigram_score = bigram.get_scoring(sentence)
    unigram_seq, unigram_score = unigram.get_scoring(sentence)
    score = unigram_score
    for k, v in bigram_score.items():
        score[k] += v
    temp = {}
    for k, v in score.items():
        if v > 0:
            temp[k] = 1
        else:
            temp[k] = 0
    score = temp
    all_clauses = []
    if len(bigram_seq):
        clause = bigram_seq[0]
        prev_score = score[bigram_seq[0]] 
        for _ in bigram_seq[1:]:
            if score[_] == prev_score:
                clause = clause + " " + _
            else:
                if prev_score == 1:
                    clause = '<span class="highlight">' + clause + "</span>"
                all_clauses.append(clause)
                clause = _
                prev_score = score[_]
        if score[bigram_seq[-1]] == 1:
            all_clauses.append('<span class="highlight">' + clause + "</span>")
        text = " ".join(all_clauses)
    else:
        text = ""
    all_codes = []
    data_qmap = qmap_bagged_concepts(pre(sentence),{})
    for k, v in data_qmap.items():
        for _ in v:
            code, acc = coder.get_icd_and_score(_)
            if float(acc) > 0.7: 
                all_codes.append(code)
    return jsonify({'text': text, 'icd': list(set(all_codes))})

if __name__ == "__main__":
    app.run()