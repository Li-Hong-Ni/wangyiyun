"""
requests超时重试函数

"""

import requests



def requestsRetry(url,headers=None,maxCount=10,timeout=20,method='get',data=None,allow_redirects=True):
    flag = True
    count = 0
    while flag:
        try:
            if method == 'get':
                r = requests.get(url,headers=headers,timeout=timeout,allow_redirects=allow_redirects)
            elif method =='post':
                r = requests.post(url, headers=headers,data=data,timeout=timeout,allow_redirects=allow_redirects)
            flag = False
        except:
            count += 1
            print('网络错误，重试*'+str(count))
            if count == maxCount:
                flag = False
                return 'error network'
    return r

