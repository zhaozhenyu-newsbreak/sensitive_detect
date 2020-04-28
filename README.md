# SENSITIVE DOC DETECTION SERVER
simple tornado web http service for python
接口地址：
http://sensitive-detect.default.svc.k8sc1.nb.com:9111/api/v0/sensitive


调用方法：
post


调用参数：json型
参数名

类型

备注

docid

string

非必须，没有docid，可以用url代替

seg_title

string

必须，以空格切分好的标题，没有标题请传空字符串

seg_content

string

必须，以空格切分好的正文，没有正文请传空字符串

text_category

dict 

必须，示例：{'second_cat': {'PoliticsGovernment_Federal': 0.8570064902305603}, 'first_cat': {'PoliticsGovernment': 0.8570064902305603}}

没有分类，请传空字典{}

url

string

必须，没有url，传空字符串


返回参数：json型
字段名

类型

备注

label

int

1为色情，0为正常

score

float

色情分数

keywords

dict

标题、正文、1级和2级关键词命中情况

code

int

0为正常，-1为服务出错

 
