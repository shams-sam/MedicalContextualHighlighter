from keras.layers import Dense, Input, LSTM, Embedding, Dropout
from keras.layers.normalization import BatchNormalization
from keras.models import Model
from keras.preprocessing.sequence import pad_sequences
from keras.layers.merge import concatenate
from keras.utils import to_categorical
import numpy as np
import _pickle as pkl
import gensim
from preprocessing import text_preprocessing

EMBEDDING_DIM = 200
WORD2VEC_MODEL = '/data/Discharge_Summary/Diagnosis_ICD/master/wikipedia-pubmed-and-PMC-w2v.bin'
NGRAM = 1
NUM_CLASSES = 2
num_lstm = 234
num_dense = 142
rate_drop_lstm = 0.21
rate_drop_dense = 0.24
act = 'relu'

class Highlighter_Unigram:
    def init(self, w2v_model=None):
        self.init_tokenizer()
        self.init_word2vec(w2v_model)
        self.init_embedding_matrix()
        self.init_model() 
    
    def init_tokenizer(self):
        print("loading tokenizer ...")
        self.data_tokenizer = pkl.load(open('unigram_data_tokenizer.pkl', 'rb'))
        self.data_index = {v: k for k, v in self.data_tokenizer.word_index.items()}
        self.data_index[0] = '***'
        
    def init_word2vec(self, w2v_model = None):
        print("loading word2vec ...")
        if w2v_model == None:
            self.w2v_model = gensim.models.KeyedVectors.load_word2vec_format(WORD2VEC_MODEL, binary=True)
        else:
            self.w2v_model = w2v_model
        
    def init_embedding_matrix(self):
        def embedding_index(word):
            return self.w2v_model.word_vec(word)
        self.nb_words = len(self.data_tokenizer.word_index)+1
        print("creating embedding matrix ...")
        self.embedding_matrix = np.zeros((self.nb_words, EMBEDDING_DIM))
        for word, i in self.data_tokenizer.word_index.items():
            if word in self.w2v_model.vocab:
                self.embedding_matrix[i] = embedding_index(word)
        print('Null word embeddings: %d' % np.sum(np.sum(self.embedding_matrix, axis=1) == 0))
    
    def init_model(self):
        print("initializing model ...")
        embedding_layer = Embedding(self.nb_words,
                EMBEDDING_DIM,
                weights=[self.embedding_matrix],
                input_length=NGRAM,
                trainable=False)
        lstm_layer = LSTM(num_lstm, dropout=rate_drop_lstm, recurrent_dropout=rate_drop_lstm)

        sequence_input = Input(shape=(NGRAM,), dtype='int32')
        embedded_sequences = embedding_layer(sequence_input)
        x = lstm_layer(embedded_sequences)
        x = BatchNormalization()(x)
        x = Dropout(rate_drop_dense)(x)

        x = Dense(num_dense, activation=act)(x)
        x = BatchNormalization()(x)
        x = Dropout(rate_drop_dense)(x)

        preds = Dense(NUM_CLASSES, activation='softmax')(x)

        model = Model(inputs=[sequence_input], \
                outputs=preds)
        model.compile(loss='categorical_crossentropy',
                optimizer='adam',
                metrics=['acc'])

        model.load_weights('unigram_model_D20171216_T2131_234_142_0.21_0.24.h5')
        self.model = model
    
    def get_prediction(self, sentence, start_tag = "[", end_tag = "]"):
        sentence = text_preprocessing(sentence)
        seq = self.data_tokenizer.texts_to_sequences([sentence])
        seq = seq[0]
        result = []
        insert_end = False
        insert_start = True
        result = []
        prev_word = None
        for idx in range(0, len(seq)):
            category = self.model.predict(np.atleast_2d([seq[idx: idx+1]]))
            cat = category.argmax()
            result.append([self.data_index[seq[idx]], cat])
        string_result = []
        for _ in result:
            if _[1] == 1 and insert_start:
                string_result.append(start_tag)
                string_result.append(_[0])
                insert_end = True
                insert_start = False
                prev_word = _[0]
            elif _[1] == 0 and insert_end:
                string_result.append(_[0])
                string_result.append(end_tag)
                insert_end = False
                insert_start = True
            else:
                string_result.append(_[0])
        if result[-1][1] == 1:
            string_result.append(end_tag)
        return " ".join(string_result)
    
    def get_scoring(self, sentence):
        sentence = text_preprocessing(sentence)
        seq = self.data_tokenizer.texts_to_sequences([sentence])
        seq = seq[0]
        word_seq = [self.data_index[_] for _ in seq]
        word_score = {}
        for idx in range(0, len(seq)):
            category = self.model.predict(np.atleast_2d([seq[idx: idx+NGRAM]]))
            cat = category.argmax()
            word_score[self.data_index[seq[idx]]] = word_score.get(self.data_index[seq[idx]], 0) + cat
        return word_seq, word_score