import requests
from flask import Flask, render_template,request
import re
import math
from bs4 import BeautifulSoup
import time
from numpy.linalg import norm
import numpy
app = Flask(__name__)
urls=[]
clean_url=[]
url_word = []
url_time = []
tdf_word = {}
tdf_list = []
top_10 = {}
def tdf(a):
    for x in clean_url:
        process_new_sentence(x)#모든 word를 다 넣기
    tf_d = compute_tf(clean_url[a])#a만 compute하기
    idf_d = compute_idf()#각 word에 관한 idf구하기
    tf_idf_d = {}
    for word,val in tf_d.items():
        tf_idf_d[word] = val*idf_d[word]#td_idf구하기

    return tf_idf_d
def process_new_sentence(s):
    tdf_list.append(s)
    tokenized = s.split()
    for word in tokenized:
        if word not in tdf_word.keys():
            tdf_word[word]=0
        tdf_word[word] += 1
def compute_tf(s):#tf 구하기 하나의 문장안에서 단어 빈도수
    bow = set() # 중복허용 x
    wordcount_d = {}
    tokenized = s.split()#tokenized
    for tok in tokenized:#s안에 있는 단어 개수 구하기
        if tok not in wordcount_d.keys():
            wordcount_d[tok]=0
        wordcount_d[tok] += 1#++하기
        bow.add(tok)
    tf_d = {}
    for keys,counts in wordcount_d.items():
        tf_d[keys] = counts/float(len(bow))
    return tf_d

def compute_idf():#idf 구하기 공통적으로 나타나면 안됨
    dval = len(tdf_list)
    # build set of words
    bow = set()
    for i in range(0,len(tdf_list)):
        tokenized = tdf_list[i].split()
        for tok in tokenized:
            bow.add(tok)#모든 문장에있는 단어 다넣기
    idf_d = {}
    for t in bow:
        cnt = 0
        for s in tdf_list:
            if t in s.split():
                cnt += 1
        idf_d[t] = math.log10(float(dval/cnt))

    return idf_d

def cosine(a,b):
    v1=[]
    v2=[]
    word_d = {}
    tokenized = clean_url[a].split()
    for word in tokenized:
        if word not in word_d.keys():
            word_d[word] = 0
        word_d[word] += 1
    tokenized = clean_url[b].split()
    for word in tokenized:
        if word not in word_d.keys():
            word_d[word] = 0
        word_d[word] += 1

    tokenized=clean_url[a].split()
    for w in word_d.keys():
        val = 0
        for t in tokenized:
            if t == w:
                val += 1
        v1.append(val)

    tokenized = clean_url[b].split()
    for w in word_d.keys():
        val = 0
        for t in tokenized:
            if t == w:
                val += 1
        v2.append(val)
    dotpro = numpy.dot(v1,v2)
    cossimill = dotpro/(norm(v1)*norm(v2))
    return cossimill
def cleantest(readdata):
	text = re.sub('[^A-Za-z0-9" ""\\n""\\t"]','',readdata)
	return text;

def process_url(url):#url에서 단어 추출하기
    start = time.time()
    req = requests.get(url)
    soup = BeautifulSoup(req.text, 'html.parser')
    name = str(soup.find_all(['p', 'h1', 'h3', 'title', 'ul','ol']))
    name = re.sub('<.+?>', '', name, 0).strip()
    name = name.replace('\\n', "")
    urls.append(url) #urls에 추가
    clean = cleantest(name)
    toknized = clean.split()#단어추출
    clean_url.append(clean)#clean_url에 집어넣기
    count = len(toknized)
    url_word.append(count)#단어 개수 집어넣기
    processing = time.time() - start
    url_time.append(processing)#처리시간 집어넣기

@app.route('/')
def main():
    return render_template('main.html',url=urls,url_word=url_word,url_time=url_time,n = len(urls))

@app.route('/',methods=['post'])
def temp():
    url = request.form['url']
    for i in urls:
        if(url == i):
            return render_template('main.html', url=urls, url_word=url_word, url_time=url_time, n=len(urls), YoN = "실패!(중복된 url 입력)")
    process_url(url)
    print(urls)
    return render_template('main.html', url=urls, url_word=url_word, url_time=url_time, n = len(urls), YoN = "성공!")

@app.route('/result',methods=['post'])
def temp2():
    file = request.files['url']
    txt = file.read()
    lines = txt.splitlines()

    for j in lines:
        url = j.decode('utf-8')
        #파일로 올시 디코드를 해야한다
        for i in urls:
            if(url == i):
                return render_template('main.html', url=urls, url_word=url_word, url_time=url_time, n=len(urls),
                                       YoN="실패!(중복된 url 입력)")
        process_url(url)
        print(urls)
    return render_template('main.html', url=urls, url_word=url_word, url_time=url_time, n=len(urls), YoN="성공!")


@app.route('/cosine',methods=['post'])
def cos_smillar():
    i = int(request.form['i'])
    cos = []
    top_3 = []
    for x in range(0, len(clean_url)):
        if x != i:
            cos.append(cosine(x, i))  # i 빼고 검사해서 cos에 넣기

    count = 0
    if (len(cos) >= 3):
        while count != 3:  # 상위 3개만 출력
            large = cos[0]  # large 초기화
            index = 0  # index는 큰상수
            for x in range(0, len(cos)):
                if large < cos[x]:
                    index = x  # index바꾸기
            cos[index] = 0
            if (index >= i):  # i와 같고 클시에는 i는 cos에 포함 되어있지 않기 때문에 +1 해서 url 출력하기
                index += 1
            print(urls[index])
            top_3.append(urls[index])
            count += 1
    else:
        top_3.append("fail: not enough urls, input at least 4 urls")

    return render_template('cosine.html',top_3 = top_3)

@app.route('/word', methods =['post'])
def tdf_if_top10():
    i = int(request.form['i'])
    top_word = []
    tdfif_word = tdf(i)
    count = 0
    if (len(urls) >= 4):
        while count != 10:
            large = 0
            index = 0
            for x, y in tdfif_word.items():
                if large < y:
                    large = y
                    index = x
            top_10[index] = large
            tdfif_word[index] = 0
            print(index, large)
            top_word.append(index)
            count += 1
    else:
	top_word.append("fail: not enough urls, input at least 4 urls")
    return render_template('word.html',top_word = top_word)

if __name__ == '__main__':
    # urls = ['http://db.apache.org/','http://buildr.apache.org/','https://jena.apache.org/','http://archiva.apache.org/']
    #url 예시들기


    app.run()
