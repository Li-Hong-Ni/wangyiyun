"""
网易云歌手列表： https://music.163.com/#/discover/artist

1 爬取歌手列表，获得每个歌手的每个分类链接（华语男歌手，华语女歌手...）
2 爬取分类链接 获得每个每个分类链接下的A-Z分类地址 例如:https://music.163.com/#/discover/artist/cat?id=1001&initial=72
3 爬取每个A-Z分类链接下的歌手信息（歌手的页面地址，歌手名字）
4 通过歌手地址解析歌手ID,再通过ID+歌手名字的形式搜索

网易云API（抓包破解得到）

1 搜索
    url: 'http://music.163.com/api/search/pc'
    method: post
    data: {
    's':'名字',         #要搜索的名字
    'offset' : 'num',  #翻页偏移量
    'total' : True     #返回全部歌曲
    'limit' : num,     #单次返回限制 最大100
    'type' : num       #搜索类型 1是单曲
    }

2 获得歌曲信息
    url: 'http://music.163.com/api/song/detail/?id={id}&ids=%5B{id}%5D'   #ID为歌曲的ID
    method : get

3 获得歌词
    url: 'http://music.163.com/api/song/lyric?os=pc&id={id}&lv=-1&kv=-1&tv=-1'   #ID为歌曲的ID

4 获取直链
    url: 'http://music.163.com/song/media/outer/url?id=[ID].mp3'  ID为歌曲的ID

播放器界面: pyqt5
"""
from requests_retry import requestsRetry
from bs4 import BeautifulSoup as bs
import header
import queue
from json import loads
from requests import get
import threading


webUrl = 'https://music.163.com'
count = 0
singerQueue = queue.Queue()
songQueue = queue.Queue()
songInfo = queue.Queue()

def get_singerClassify():                   #获取歌手分类的链接
    url = "https://music.163.com/discover/artist"
    headers = header.header()
    r = requestsRetry(url,headers=headers,maxCount=10,timeout=30).text
    html = bs(r,'html.parser')
    singerClassify = html.select('div[class="g-bd2 f-cb"] div[class="g-sd2"] div[class="g-wrap4 n-sgernav"] div[class="blk"] a')
    for s in singerClassify:
        #singerType = s.get_text()
        singerTypeLink = webUrl+s.get('href')
        singerTypeLink = singerTypeLink.replace(' ','')
        get_allSingers(singerTypeLink)


def get_allSingers(singerTypeLink):        #获取歌手分类下的分类链接
    headers = header.header()
    r = requestsRetry(singerTypeLink, headers=headers, maxCount=10, timeout=30).text
    html = bs(r,'html.parser')
    singerClassifyA_Z = html.select('div[class="g-wrap"] ul[class="n-ltlst f-cb"] li a')
    singerClassifyA_Z.pop(0)
    for s in singerClassifyA_Z:
        singerLinkA_Z = webUrl+s.get('href').replace(' ','')
        get_singerUrl(singerLinkA_Z)


def get_singerUrl(singerLinkA_Z):           #获取每个歌手的ID和名字
    headers = header.header()
    r = requestsRetry(singerLinkA_Z, headers=headers, maxCount=10, timeout=30).text
    html = bs(r,'html.parser')
    singerUrls = html.select('div[class="m-sgerlist"] ul li a[class="nm nm-icn f-thide s-fc0"]')
    for s in singerUrls:
        singerUrl = webUrl+s.get('href').replace(' ','')
        singerName = s.get_text()
        singerID = singerUrl.split('=')[-1]
        global count
        count+=1
        singerInfo = {
            'singerName' : singerName,
            'singerID' : singerID
        }
        singerQueue.put(singerInfo)
        print(count,singerName,singerUrl)



def search_songs(singerInfo):         #根据歌手的名字搜索它所有的歌
    headers = header.header()
    url = 'http://music.163.com/api/search/pc'

    songsInfo = {}
    flag = True
    pageNum = 0
    while flag:
        limit = 30
        offset = str(pageNum*30)
        data = {
            's' : singerInfo['singerName'],
            'offset' : offset,     #第一页为0，第二页为30.... 等于(页数-1)*limit
            'total' : True,
            'limit' : limit,
            'type' : 1
        }

        r = requestsRetry(url=url,method='post',data=data,headers=headers).text
        r = loads(r,encoding='utf-8')
        try:
            songs = r['result']['songs']
            for song in songs:
                songName = song['name']
                songID = song['id']
                songsInfo[songID] = songName
        except KeyError:
            flag = False
        pageNum += 1
    return songsInfo




def get_lyric(songID):
    headers = header.header()
    songID = str(songID)
    url = 'http://music.163.com/api/song/lyric?os=pc&id={id}&lv=-1&kv=-1&tv=-1'.format(id=songID)
    r = requestsRetry(url=url,method='get',headers=headers).text
    r = loads(r,encoding='utf-8')
    lrc = r['lrc']['lyric']
    return lrc



def get_realLink(songID):
    songID = str(songID)
    url = 'https://music.163.com/song/media/outer/url?id={id}.mp3'.format(id=songID)

    r = get(url,headers=header.header(),allow_redirects=False)
    if not r.url == 'https://music.163.com/404':
        return r.url
    else:
        return 'https://music.163.com/404'


