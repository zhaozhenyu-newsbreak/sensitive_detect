#!/usr/bin/env python
#-*- coding:UTF-8 -*-
#########################################################################
# File Name: test.py
# Author: NLP_zhaozhenyu
# Mail: zhaozhenyu_tx@126.com
# Created Time: 15:28:36 2019-01-25
#########################################################################
import sys
import requests
import json
import time

from pymongo import MongoClient
staticfeature = MongoClient('172.31.24.51',27017,unicode_decode_error_handler='ignore')['staticFeature']['document']
url_prefix = 'http://sensitive-detect.default.svc.k8sc1.nb.com:9111/api/v0/sensitive'
#url_prefix = 'http://172.31.128.129:9111/api/v0/category_classification_dnn'
#url_prefix = 'http://text-category-dnn.default.svc.k8sc1.nb.com:9111/api/v0/category_classification_dnn'
#url_prefix = 'http://text-category-dnn.ha.nb.com:9111/api/v0/category_classification_dnn'
docid = sys.argv[1]
documents = staticfeature.find({'_id':docid})
if documents !=None:
    for doc in documents:
        docinfo = {}
        docinfo['docid'] = doc['_id']
        docinfo['url'] = doc['url']
        docinfo['seg_title'] = doc['stitle']
        docinfo['seg_content'] = doc['seg_content']
        docinfo['text_category'] = doc['text_category']
        print(docinfo)
        print(doc['text_category'])
        return_info = requests.post(url_prefix,json = docinfo)
        return_dict = json.loads(return_info.text)
        print(str(return_dict)+'\t'+docinfo['docid'])

