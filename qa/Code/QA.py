import warnings
warnings.filterwarnings('ignore')
import pickle
import pandas as pd
from textblob import TextBlob
import torch
import re
from InferSent import models


class QA:
    def readComprehensionAndQuestions(self):
        comprehension = pd.read_excel("../Data/permits.xlsx")
        i = 0
        for index, rows in comprehension.iterrows():
            comprehension.loc[i,'context'] = re.sub(r'\n', ' ', rows['context'])
            i = i+1
        paras = list(comprehension['context'].drop_duplicates().reset_index(drop= True))
        blob = TextBlob(" ".join(paras))
        sentences = [item.raw for item in blob.sentences]
        questions_list = list(comprehension['questions'])
        return sentences, questions_list

    def initModel(self, sentences):
        GLOVE_PATH = '/Users/ravibhargava/temp/GloVe/glove.840B.300d.txt'
        MODEL_PATH = '../InferSent/encoder/infersent1.pkl'
        params_model = {'bsize': 64, 'word_emb_dim': 300, 'enc_lstm_dim': 2048,
                        'pool_type': 'max', 'dpout_model': 0.0}
        model = models.InferSent(params_model)
        from functools import partial
        import pickle
        pickle.load = partial(pickle.load, encoding="latin1")
        pickle.Unpickler = partial(pickle.Unpickler, encoding="latin1")
        model.load_state_dict(torch.load(MODEL_PATH))
        model.set_w2v_path(GLOVE_PATH)
        model.build_vocab(sentences, tokenize=True)
        return model

    def normalize(self, sentences):
        sentences_copy=sentences.copy()
        normalized_sentences=pd.DataFrame()
        normalized_sentences['cms_notes']=sentences_copy
        normalized_sentences['cms_notes'] = normalized_sentences.apply(lambda x:re.sub(r'\s+', ' ', x["cms_notes"]),axis=1)
        normalized_sentences['cms_notes'] = normalized_sentences.apply(lambda x: x['cms_notes'].lower(), axis=1)
        #Replacing numbers
        normalized_sentences['cms_notes'] = normalized_sentences.apply(lambda x:re.sub(r'(\d+/\d+/\d+)|(\d+\.\d+\.\d+)|(\d+\-\d+\-\d+)|(\d+\/\d+)|(\d+th)|(\d+nd)|(\d+rd)|(\d+st)', ' DATE ', x["cms_notes"]),axis=1)
        normalized_sentences['cms_notes'] = normalized_sentences.apply(lambda x:re.sub(r'\b(mon|tue|wed|thurs|fri|sat|sun|monday|tuesday|wednesday|thursday|friday|saturday|sunday|jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec|january|february|march|april|may|june|july|august|september|october|november|december)\b',' DATE ', x["cms_notes"]),axis=1)
        normalized_sentences['cms_notes'] = normalized_sentences.apply(lambda x:re.sub(r'(\$\d+\,\d+\.\d+)|(\$\d+\,\d+)|(\$\d+\.\d+)|(\$\d+)|(\$\ d+\,\d+\.\d+)|(\$ \d+\,\d+)|(\$ \d+\.\d+)|(\$ \d+)|(\d+\,\d+\.\d+)|(\d+\,\d+)|(\d+\.\d+)', ' AMOUNT ', x["cms_notes"]),axis=1)
        normalized_sentences['cms_notes'] = normalized_sentences.apply(lambda x:re.sub(r'(#\d+)|(# \d+)|(\d+)', ' NUMBER ', x["cms_notes"]),axis=1)
        normalized_sentences['cms_notes'] = normalized_sentences.apply(lambda x:re.sub(r'(\d+\.\d+)|(\d+)', ' AMOUNT ', x["cms_notes"]),axis=1)
        normalized_sentences['cms_notes'] = normalized_sentences.apply(lambda x:re.sub(r'[^\s]+@[^\s]+\.[^\s]+',' MAIL ', x["cms_notes"]),axis=1)
        #Removing remaining numbers and spaces
        normalized_sentences['cms_notes'] = normalized_sentences.apply(lambda x:re.sub(r'\s+', ' ', x["cms_notes"]),axis=1)
        normalized_sentences['cms_notes'] = normalized_sentences.apply(lambda x:re.sub(r'(\()|(\))', '', x["cms_notes"]),axis=1)
        #Remove punctuations
        normalized_sentences['cms_notes'] = normalized_sentences.apply(lambda x:re.sub(r'[^a-zA-Z]', ' ', x["cms_notes"]),axis=1)
        normalized_sentences['cms_notes'] = normalized_sentences.apply(lambda x:re.sub(r'\s+', ' ', x["cms_notes"]),axis=1)
        normalized_sentences['cms_notes'] = normalized_sentences.apply(lambda x: x['cms_notes'].lower(), axis=1)
        normalized_sentences_list=[]
        for i in normalized_sentences['cms_notes']:
            normalized_sentences_list.append(i)
        return normalized_sentences_list

    def encodeAndDump(self, normalized_sentences_list, questions_list, model):
        dict_embeddings = {}
        for i in range(len(normalized_sentences_list)):
            dict_embeddings[normalized_sentences_list[i]] = model.encode([normalized_sentences_list[i]], tokenize=True)
        for i in range(len(questions_list)):
            dict_embeddings[questions_list[i]] = model.encode([questions_list[i]], tokenize=True)
        d1 = {key:dict_embeddings[key] for i, key in enumerate(dict_embeddings) if i % 2 == 0}
        d2 = {key:dict_embeddings[key] for i, key in enumerate(dict_embeddings) if i % 2 == 1}
        with open('../Data/permits_1.pickle', 'wb') as handle:
            pickle.dump(d1, handle)
        with open('../Data/permits_2.pickle', 'wb') as handle:
            pickle.dump(d2, handle)
        del dict_embeddings

    def main(self):
        sentences, questions_list =self.readComprehensionAndQuestions()
        model = self.initModel(sentences)
        normalized_sentences_list = self.normalize(sentences)
        self.encodeAndDump(normalized_sentences_list, questions_list, model)


qa = QA()
qa.main()
