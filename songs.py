"""
网易云歌手列表： https://music.163.com/#/discover/artist

1 爬取歌手列表，获得每个歌手的每个分类链接（华语男歌手，华语女歌手...）
2 爬取分类链接 获得每个每个分类链接下的A-Z分类地址 例如:https://music.163.com/#/discover/artist/cat?id=1001&initial=72
3 爬取每个A-Z分类链接下的歌手信息（歌手的页面地址，歌手名字）
4 通过歌手地址解析歌手ID,再通过ID+歌手名字的形式搜索
"""
from requests_retry import requrstsRetry
from bs4 import BeautifulSoup as bs
import header
import threading
import queue

webUrl = 'https://music.163.com'
count = 0
singerQueue = queue.Queue()
songQueue = queue.Queue()
songInfo = queue.Queue()

def get_singerClassify():                   #获取歌手分类的链接
    url = "https://music.163.com/discover/artist"
    headers = header.header()
    r = requrstsRetry(url,headers=headers,maxCount=10,timeout=30)
    html = bs(r,'html.parser')
    singerClassify = html.select('div[class="g-bd2 f-cb"] div[class="g-sd2"] div[class="g-wrap4 n-sgernav"] div[class="blk"] a')
    for s in singerClassify:
        #singerType = s.get_text()
        singerTypeLink = webUrl+s.get('href')
        singerTypeLink = singerTypeLink.replace(' ','')
        get_allSingers(singerTypeLink)


def get_allSingers(singerTypeLink):        #获取歌手分类下的分类链接
    headers = header.header()
    r = requrstsRetry(singerTypeLink, headers=headers, maxCount=10, timeout=30)
    html = bs(r,'html.parser')
    singerClassifyA_Z = html.select('div[class="g-wrap"] ul[class="n-ltlst f-cb"] li a')
    singerClassifyA_Z.pop(0)
    for s in singerClassifyA_Z:
        singerLinkA_Z = webUrl+s.get('href').replace(' ','')
        get_singerUrl(singerLinkA_Z)


def get_singerUrl(singerLinkA_Z):           #获取每个歌手的ID和名字
    headers = header.header()
    r = requrstsRetry(singerLinkA_Z, headers=headers, maxCount=10, timeout=30)
    html = bs(r,'html.parser')
    singerUrls = html.select('div[class="m-sgerlist"] ul li a[class="nm nm-icn f-thide s-fc0"]')
    for s in singerUrls:
        singerUrl = webUrl+s.get('href').replace(' ','')
        singerName = s.get_text()
        singerID = singerUrl.split('=')[-1]
        singerQueue.put((singerName,singerID))


get_singerClassify()
'''
多线程部分
线程1: 爬取歌手的地址
线程2-5: 爬取歌的地址
线程6-50: 爬取歌曲的详细信息
'''

