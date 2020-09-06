# Created on Tue September 6, 2020
# Copyright (c) 2020 - Software Threads, Inc.


import numpy as np, pandas as pd
from textblob import TextBlob
import pickle
from scipy import spatial
import warnings
warnings.filterwarnings('ignore')
import re


class Process:

    def readFiles(self):
        comprehension = pd.read_excel(r'../Data/permits.xlsx')
        with open(r'../Data/permits_1.pickle', "rb") as f:
            d1 = pickle.load(f)
        with open(r'../Data/permits_2.pickle', "rb") as f:
            d2 = pickle.load(f)
        dict_embed = dict(d1)
        dict_embed.update(d2)
        del d1, d2
        return comprehension, dict_embed

    def normalize(self, sentences):
        sentences['sentences'] = sentences['context'].apply(lambda x: [item.raw for item in TextBlob(x).sentences])
        sentences['original_sentences'] = sentences['sentences']
        i = 0
        for index, row in sentences.iterrows():
            normalized_sentences = pd.DataFrame()
            normalized_sentences['sentences'] = row['sentences']
            normalized_sentences['sentences'] = normalized_sentences.apply(lambda x: re.sub(r'\s+', ' ', x['sentences']), axis=1)
            normalized_sentences['sentences'] = normalized_sentences.apply(lambda x: x['sentences'].lower(), axis=1)
            normalized_sentences['sentences'] = normalized_sentences.apply(lambda x:re.sub(r'(\d+/\d+/\d+)|(\d+\.\d+\.\d+)|(\d+\-\d+\-\d+)|(\d+\/\d+)|(\d+th)|(\d+nd)|(\d+rd)|(\d+st)', ' DATE ', x["sentences"]),axis=1)
            normalized_sentences['sentences'] = normalized_sentences.apply(lambda x:re.sub(r'\b(mon|tue|wed|thurs|fri|sat|sun|monday|tuesday|wednesday|thursday|friday|saturday|sunday|jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec|january|february|march|april|may|june|july|august|september|october|november|december)\b',' DATE ', x["sentences"]),axis=1)
            normalized_sentences['sentences'] = normalized_sentences.apply(lambda x:re.sub(r'(\$\d+\,\d+\.\d+)|(\$\d+\,\d+)|(\$\d+\.\d+)|(\$\d+)|(\$\ d+\,\d+\.\d+)|(\$ \d+\,\d+)|(\$ \d+\.\d+)|(\$ \d+)|(\d+\,\d+\.\d+)|(\d+\,\d+)|(\d+\.\d+)', ' AMOUNT ', x["sentences"]),axis=1)
            normalized_sentences['sentences'] = normalized_sentences.apply(lambda x:re.sub(r'(#\d+)|(# \d+)|(\d+)', ' NUMBER ', x["sentences"]),axis=1)
            normalized_sentences['sentences'] = normalized_sentences.apply(lambda x:re.sub(r'(\d+\.\d+)|(\d+)', ' AMOUNT ', x["sentences"]),axis=1)
            normalized_sentences['sentences'] = normalized_sentences.apply(lambda x:re.sub(r'[^\s]+@[^\s]+\.[^\s]+',' MAIL ', x["sentences"]),axis=1)
            normalized_sentences['sentences'] = normalized_sentences.apply(lambda x:re.sub(r'\s+', ' ', x["sentences"]),axis=1)
            normalized_sentences['sentences'] = normalized_sentences.apply(lambda x:re.sub(r'(\()|(\))', '', x["sentences"]),axis=1)
            normalized_sentences['sentences'] = normalized_sentences.apply(lambda x:re.sub(r'[^a-zA-Z]', ' ', x["sentences"]),axis=1)
            normalized_sentences['sentences'] = normalized_sentences.apply(lambda x:re.sub(r'\s+', ' ', x["sentences"]),axis=1)
            normalized_sentences['sentences'] = normalized_sentences.apply(lambda x:re.sub(r'\.', '', x["sentences"]),axis=1)
            normalized_sentences['sentences'] = normalized_sentences.apply(lambda x: x['sentences'].lower(), axis=1)
            sentences.loc[i,'sentences']=list(normalized_sentences['sentences'])
            i=i+1
            sentences['sent_emb'] = sentences['sentences'].apply(lambda x: [dict_emb[item][0] if item in dict_emb else np.zeros(4096) for item in x])
            sentences['quest_emb'] = sentences['questions'].apply(lambda x: dict_emb[x] if x in dict_emb else np.zeros(4096) )
        return sentences

    def cosine_sim(self,x):
        li = []
        for item in x["sent_emb"]:
            li.append(spatial.distance.cosine(item,x["quest_emb"][0]))
        return li

    def pred_idx(self, distances):
        return np.argmin(distances)

    def predictions(self, train):
        train["cosine_sim"] = train.apply(self.cosine_sim, axis = 1)
        train["diff"] = (train["quest_emb"] - train["sent_emb"])**2
        train["euclidean_dis"] = train["diff"].apply(lambda x: list(np.sum(x, axis = 1)))
        del train["diff"]
        train["pred_idx_cos"] = train["cosine_sim"].apply(lambda x: self.pred_idx(x))
        train["pred_idx_euc"] = train["euclidean_dis"].apply(lambda x: self.pred_idx(x))
        return train

    def generateAnswers(self, repo):
        predicted = self.predictions(repo)
        ques=[]
        answer_cos=[]
        answer_euc=[]
        cosine=[]
        euc=[]
        for i in range(len(predicted)):
            answer_cos.append(predicted.loc[i,'original_sentences'][predicted.loc[i,'pred_idx_cos']])
            answer_euc.append(predicted.loc[i,'original_sentences'][predicted.loc[i,'pred_idx_euc']])
            ques.append(predicted.loc[i,'questions'])
            cosine.append(predicted.loc[i,'cosine_sim'][predicted.loc[i,'pred_idx_cos']])
            euc.append(predicted.loc[i,'euclidean_dis'][predicted.loc[i,'pred_idx_euc']])
        df=pd.DataFrame()
        df['Question']=ques
        df['Answer_Cos']=answer_cos
        df['Cosine Sim']=cosine
        df['Answer_Euc']=answer_euc
        df['Euclidean Dis']=euc
        df.to_csv(r'../Results/permits.csv')


process = Process()
comp, dict_emb = process.readFiles()
repo = process.normalize(comp)
process.generateAnswers(repo)
