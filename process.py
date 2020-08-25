#!/usr/bin/env python
#-*- coding:UTF-8 -*-
#########################################################################
# File Name: process.py
# Author: NLP_zhaozhenyu
# Mail: zhaozhenyu_tx@126.com
# Created Time: 15:41:54 2019-01-25
#########################################################################
import sys
import re
import numpy as np
from nltk.stem import PorterStemmer 
from nltk.tokenize import word_tokenize
ps = PorterStemmer() 





def get_local_diction(path):
    res = {}
    cur = 0
    for lines in open(path):
        res[lines.strip().split('\t')[0]] = cur
        cur +=1
    return res

#for monica
forbid_for_monica = get_local_diction('./dict/forbid_for_monica.dict')


def get_embedding_dict(path,dim):
    res = {}
    for lines in open(path):
        data = lines.strip().split(' ',1)
        em_str = data[1].split(' ')
        if len(em_str)<dim:
            continue
        cur = []
        for i in em_str:
            cur.append(float(i))
        res[data[0]] = cur
    return res

def get_value_dict(path):
    res = {}
    for lines in open(path):
        data = lines.strip().split('\t')
        res[data[0]] = float(data[1])
    return res
    
def ngram_dict(path):
    res = {}
    for lines in open(path):
        data = lines.strip()
        res[data] = 1
    return res

def get_word_dict(words,stopwords):
    pat = '(\.|\?|-|:|&|/)'
    res = {}
    for word in words:
        for span in re.split(pat,word):
            if span != '' and span!= ' ' and span not in stopwords:
                try:
                    int(span)
                    continue
                except:
                    if span in res:
                        res[span] +=1
                    else:
                        res[span] = 1

    return res

def is_in_ngram(words,dic):
    res = {}
    for word in words:
        if word in dic:
            res[word] = 1
    doc = ' '.join(words)
    for key in dic:
        if len(key.split(' '))>1:
            if key in doc:
                res[key] = 1
    return res


def preprocess(content,forbidden_strict,forbidden_nostrict,stopwords):
    '''
    preprocessing content
    return:
        word_dict: key is the word,value is num
        keywords_dict:{'strict':{}} where value is also a set type
    '''
    words = content.lower().split(' ')
    word_dict = get_word_dict(words,stopwords)
    keywords_dict = {'strict':is_in_ngram(words,forbidden_strict),'nostrict':is_in_ngram(words,forbidden_nostrict)}
    return word_dict,keywords_dict


def get_embedding_feature(words,embedding,dim,idf_dict):
    res = np.zeros(dim)
    sum_ = 0.0
    for word in words:
        if word in idf_dict and word in embedding:
            res += words[word]*idf_dict[word]*np.array(embedding[word])
            sum_ += words[word]*idf_dict[word]
    if sum_ >0:
        res = res/sum_
    return res

def get_category_onehot(category,cate_dict):
    res = [ 0 for i in range(len(cate_dict))]
    if category ==None:
        return res,False
    cate = category.get('first_cat')
    if cate!=None and ('Crime' in cate or 'Politics' in cate):
        return res,True
    if cate !=None:
        first_cat = list(cate.keys())[0]
        if first_cat in cate_dict:
            res[cate_dict[first_cat]] = 1
    return res,False

def get_keywords_flag(content_keywords,title_keywords):
    if len(title_keywords['strict'])>0:
        return 1
    elif len(title_keywords['nostrict'])>=2 or len(content_keywords['strict'])+len(content_keywords['nostrict'])>=5:
        return 2
    elif len(title_keywords['nostrict']) + len(content_keywords['strict'])+len(content_keywords['nostrict'])==0:
        return 4
    else:
        return 3


def judge(content_keywords,title_keywords,forbidden_ex,py):
    t_s = len(title_keywords['strict'])
    t_n = len(title_keywords['nostrict'])
    c_s = len(content_keywords['strict'])
    c_n = len(content_keywords['nostrict'])
    for k in forbidden_ex:
        if k in title_keywords['strict']:
            return 1
        elif k in title_keywords['nostrict']:
            return 1

    if py>0.5 and t_s+t_n+c_s+c_n >0:
        if py>0.9:
            return 1
        elif t_s+t_n+c_s+c_n >1:
            return 1
    return 0


def is_monica_adult(title):
    doc = title.lower().split(' ')
    for word in doc:
        if word in forbid_for_monica:
            return True,word
    return False,''



def process(model,idf_dict,embedding,dim,content,category,title,url,forbidden_strict,forbidden_nostrict,cate_dict,stopwords,fobidden_ex):
    '''
    main processing function：
    idf_dict:idf weighting，dict
    embedding:glove embedding，dict，300d
    dim : 300 default
    content: string, splited by blanket
    category: text_category, dict
    title: string
    url:url string
    forbidden_strict: keywords that are serious,dict,key is firstword ,value is list of rest words{porn:[videos,pic]}
    forbidden_nostrict: keywords that may have relation with sex,dict
    '''
    #preprocess for is_in keywords,counts
    content_words,content_keywords = preprocess(content,forbidden_strict,forbidden_nostrict,stopwords)
    title_words,title_keywords = preprocess(title,forbidden_strict,forbidden_nostrict,stopwords)
    url_words,url_keywords = preprocess(url,forbidden_strict,forbidden_nostrict,stopwords)
    #feature
    input_x = []
    input_x.extend(get_embedding_feature(content_words,embedding,dim,idf_dict))
    input_x.extend(get_embedding_feature(title_words,embedding,dim,idf_dict))
    input_x.extend(get_embedding_feature(url_words,embedding,dim,idf_dict))
    cate_fea,flag = get_category_onehot(category,cate_dict)
    input_x.extend(cate_fea)
    #keywords_flag = get_keywords_flag(content_keywords,title_keywords)

    #predict
    py = model.predict_proba([input_x])[0][1]

    label = judge(content_keywords,title_keywords,fobidden_ex,py)
    #犯罪类，政府类排除
    if flag:
        label = 0
    title_stem = ' '.join([ps.stem(w) for w in title_words.keys()])
    #title_stem = ' '.join([ps.stem(w) for w in word_tokenize(title)])
    #title_stem_keywords = get_word_dict(title_stem.lower().split(' '),stopwords)
    #title_stem = ' '.join(list(title_stem_keywords.keys()))
    monica_adult_res ,monica_adult_word = is_monica_adult(title_stem)
    res = {'label':label,'score':py,
           'keywords':{'content_keywords':content_keywords,'title_keywords':title_keywords},
           'is_adult_title':monica_adult_res,'adult_title_word':monica_adult_word}

    return res
