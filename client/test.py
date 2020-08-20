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

#url_prefix = 'http://172.31.142.68:9111/api/v0/sensitive'
url_prefix = 'http://sensitive-detect.default.svc.k8sc1.nb.com:9111/api/v0/sensitive'
url_prefix = 'http://0.0.0.0:9111/api/v0/sensitive'

test_file = sys.argv[1]

start = time.time()

for lines in open(test_file):
    data = lines.strip().split('\t')
    docinfo = json.loads(data[2])
    docinfo['seg_title'] = docinfo['title']
    docinfo['seg_content'] = docinfo['content']
    return_info = requests.post(url_prefix,json = docinfo)
    return_dict = json.loads(return_info.text)
    #print(data[0]+'\t'+str(return_dict['label'])+'\t'+json.dumps(return_dict))
    if  return_dict['is_monica_adult_title']:
        print(str(return_dict)+'\t'+lines.strip())
print(time.time()-start)
