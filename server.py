#!/usr/bin/env python
#-*- coding:UTF-8 -*-
#########################################################################
# File Name: server.py
# Author: NLP_zhaozhenyu
# Mail: zhaozhenyu_tx@126.com
# Created Time: 14:45:17 2019-01-25
#########################################################################
import sys
import tornado.ioloop
import tornado.options
import tornado.web
import getopt
from configparser import ConfigParser
from logger import getLoggers
import logging
import os
import json
import requests
import traceback
import sklearn
import pickle

import process

model = pickle.load(open('./model/GBDT.MODEL4','rb'))
stopwords = process.get_local_diction('./dict/stopword_en.txt')
idf_dict = process.get_value_dict('./dict/idf.dict')
embedding = process.get_embedding_dict('../top50w.embedding',300)
forbidden_strict = process.ngram_dict('./dict/forbidden_strict')
forbidden_nostrict = process.ngram_dict('./dict/forbidden_nostrict')
cate_dict = process.get_local_diction('./dict/cate_dict')


print('local file loaded')





class MainHandler(tornado.web.RequestHandler):
    """
    测试路由
    """
    def get(self):
        self.finish('NB - NLP - SENSITIVE\n')

class ProcessHandler(tornado.web.RequestHandler):
    """
    计算
    """
    def post(self):
        response_dict = {'code': -1,'label':0,'score':'0.0','keywords':[]}
        docid = 'no_id'
        try:
            data_dict = json.loads(self.request.body)
            ##get parameters
            docid = data_dict.get('docid')
            if docid ==None:
                docid = 'no_id'
            title = data_dict.get('seg_title')
            if title == None:
                title = ''
            content = data_dict.get('seg_content')
            if content == None:
                content = ''
            category = data_dict.get('text_category')
            if category == None:
                category = {}
            url = data_dict.get('url')
            if url == None:
                url = ''
            args_dict = {'docid':docid,'title':title,'category':category,'url':url}
            logArgs.info(str(args_dict))
            #process
            result = process.process(model,idf_dict,embedding,300,content,category,title,url,forbidden_strict,forbidden_nostrict,cate_dict,stopwords)
            #result
            result["code"] = 0
            result["docid"] = docid
            response_dict_string = json.dumps(result, ensure_ascii=False)
            logOutput.info('server\t%s\t%s' % (docid, response_dict_string))
            self.finish(response_dict_string)
        except Exception as e:
            msg = str(traceback.format_exc())
            response_dict_string = json.dumps(response_dict, ensure_ascii=False)
            logError.error('server\t%s\t%s' % (docid, str(msg)))
            logOutput.info('server\t%s\t%s' % (docid, response_dict_string))
            self.finish(response_dict_string)

    def get(self):
        response_dict = {'code': -1,'label':0,'score':'0.0','keywords':[]}
        docid = 'no_id'
        try:
            ##get parameters
            docid = self.get_argument('docid')
            title = self.get_argument('seg_title')
            content = self.get_argument('seg_content')
            category = eval(self.get_argument('text_category'))
            url = self.get_argument('url')
            args_dict = {'docid':docid,'title':title,'category':category,'url':url}
            logArgs.info(str(args_dict))
            #process
            result = process.process(model,idf_dict,embedding,300,content,category,title,url,forbidden_strict,forbidden_nostrict,cate_dict,stopwords)
            #result
            result["code"] = 0
            result["docid"] = docid
            response_dict_string = json.dumps(result, ensure_ascii=False)
            logOutput.info('server\t%s\t%s' % (docid, response_dict_string))
            self.finish(response_dict_string)
        except Exception as e:
            msg = str(traceback.format_exc())
            response_dict_string = json.dumps(response_dict, ensure_ascii=False)
            logError.error('server\t%s\t%s' % (docid, str(msg)))
            logOutput.info('server\t%s\t%s' % (docid, response_dict_string))
            self.finish(response_dict_string)

def run():
    app = tornado.web.Application(
        [
         (r"/api/v0/sensitive", ProcessHandler),
         (r"/ndp/online", MainHandler),
         (r"/ndp/offline", MainHandler),
         (r"/ndp/status", MainHandler),
         (r"/ndp/check", MainHandler)
         ])
    
    server = tornado.httpserver.HTTPServer(app)
    logService.info('Instance {0} start successfully'.format(SERVER_PORT))
    print('Instance {0} start successfully'.format(SERVER_PORT))
    server.bind(SERVER_PORT)
    server.start(8)
    tornado.ioloop.IOLoop.instance().start()


def usage():
    print('usage: python server.py -f config.ini -p 9003')


def read_conf(conf_file):
    """
    读取配置文件
    :param conf_file:
    :return:
    """
    global SERVER_PORT, LOG_PATH, logService, logArgs, logOutput, logError, logFormatError, logDebug
    try:
        if configfile == "" or not configfile:
            return False
        cfg = ConfigParser()
        cfg.read(configfile)
        current_path = os.path.abspath(__file__)
        father_path = os.path.abspath(os.path.dirname(current_path) + os.path.sep + ".")
        LOG_PATH = cfg.get('server', 'log_path')
        LOG_PATH = os.path.normpath(LOG_PATH + os.path.sep + str(SERVER_PORT))  # 绝对路径
        if not os.path.exists(LOG_PATH):
            os.makedirs(LOG_PATH)
        logService = getLoggers('logService', logging.INFO, LOG_PATH + '/service.log')
        logArgs = getLoggers('logArgs', logging.INFO, LOG_PATH + '/args.log')
        logOutput = getLoggers('logOutput', logging.INFO, LOG_PATH + '/output.log')
        logError = getLoggers('logError', logging.INFO, LOG_PATH + '/error.log')
        logDebug = getLoggers('logDebug', logging.INFO, LOG_PATH + '/debug.log')
    except Exception as e:
        print(str(traceback.format_exc()))
        print('read config file failed')
        return False
    return True


if __name__ == "__main__":
    """
    每个进程有一个配置文件（日志地址）
    """
    global SERVER_PORT
    try:
        if(len(sys.argv[1:]) == 0):
            usage()
        opts, args = getopt.getopt(sys.argv[1:], 'hf:p:')
        configfile = ''
        for opt, arg in opts:
            if opt == '-f':
                configfile = arg
            elif opt == '-p':
                SERVER_PORT = int(arg)
            elif opt == '-h':
                usage()
            else:
                usage()
        if not read_conf(configfile):
            print('invalid config file')
            exit(1)
        run()
    except (IOError, getopt.GetoptError) as err:
        print(str(err))
        exit(1)


