import os
import configparser
import requests
from bs4 import BeautifulSoup
import time
import ddddocr

ocr = ddddocr.DdddOcr(beta=True, show_ad = False)

max_attempt = 20
username = None
password = None
u_ip = None

ac_ip = "10.13.7.59"
pushPageId = "5bf74194-d2a8-4bb8-ac6b-8ff3e855f6a7"
ssid = "PUxzd1NzaWRQbGFjZWhvbGRlcj0="
url_prefix = "https://net-auth.shanghaitech.edu.cn:19008/portalpage/04b92f0a808c4d10b572642e3be564b2/20221024095238/pc/auth.html"
refer_url = url_prefix + "?ac-ip={acip}&uaddress={uip}&umac=null&authType=1&lang=zh_CN&ssid={sid}&pushPageId={pid}".format(acip=ac_ip, uip = u_ip, sid = ssid,pid = pushPageId)

def get_user_config():
    config = configparser.ConfigParser()
    config.read('config.ini')
    
    username = config.get('UserConfig', 'username')
    password = config.get('UserConfig', 'password')
    u_ip = config.get('UserConfig', 'u_ip')
    
    return username, password, u_ip

def set_user_config(username, password, u_ip):
    config = configparser.ConfigParser()
    config.read('config.ini')
    
    if(not config.has_section('UserConfig')):
        config.add_section('UserConfig')
    config.set('UserConfig', 'username', username)
    config.set('UserConfig', 'password', password)
    config.set('UserConfig', 'u_ip', u_ip)
    
    with open('config.ini', 'w') as config_file:
        config.write(config_file)



def AcquireInternet(validcode:str) -> bool :

    headers = {
    'Accept': 'application/json, text/javascript, */*; q=0.01',
    'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
    'Cache-Control': 'no-cache',
    'Connection': 'keep-alive',
    'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
    'DNT': '1',
    'Origin': 'https://net-auth.shanghaitech.edu.cn:19008',
    'Pragma': 'no-cache',
    'Referer': refer_url,
    'Sec-Fetch-Dest': 'empty',
    'Sec-Fetch-Mode': 'cors',
    'Sec-Fetch-Site': 'same-origin',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36 Edg/113.0.1774.50',
    'sec-ch-ua': '"Microsoft Edge";v="113", "Chromium";v="113", "Not-A.Brand";v="24"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
}

    data = {
    'pushPageId': pushPageId,
    'userPass': password,
    'esn': '',
    'apmac': '',
    'armac': '',
    'authType': '1',
    'ssid': ssid,
    'uaddress': u_ip,
    'umac': 'null',
    'accessMac': '',
    'businessType': '',
    'acip': ac_ip,
    'agreed': '1',
    'registerCode': '',
    'questions': '',
    'dynamicValidCode': '',
    'dynamicRSAToken': '',
    'validCode': validcode,
    'userName': username,
}
    try:
        response = requests.post('https://net-auth.shanghaitech.edu.cn:19008/portalauth/login', headers=headers, data=data)
    except Exception as e:
        print(e)
        return False

    time.sleep(3)
    return testInternet()

def getValidCode() -> str:
    timestamp = int(round(time.time() * 1000))
    # url = "https://net-auth.shanghaitech.edu.cn:19008/portalauth/verificationcode?date={t}&uaddress={uip}&umac=null&acip={acip}".format(t=timestamp,uip=u_ip,acip=ac_ip)

    img_headers = {
    'Accept': 'image/webp,image/apng,image/svg+xml,image/*,*/*;q=0.8',
    'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
    'Cache-Control': 'no-cache',
    'Connection': 'keep-alive',
    # 'Cookie': 'PSESSIONID=',
    'DNT': '1',
    'Pragma': 'no-cache',
    'Referer': refer_url,
    'Sec-Fetch-Dest': 'image',
    'Sec-Fetch-Mode': 'no-cors',
    'Sec-Fetch-Site': 'same-origin',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36 Edg/113.0.1774.50',
    'sec-ch-ua': '"Microsoft Edge";v="113", "Chromium";v="113", "Not-A.Brand";v="24"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
}

    params = {
    'date': timestamp,
    'uaddress': u_ip,
    'umac': 'null',
    'acip': ac_ip,
}

    img_response = requests.get(
    'https://net-auth.shanghaitech.edu.cn:19008/portalauth/verificationcode',
    params=params,
    headers=img_headers,
)
 
    img = img_response.content
    ocr.set_ranges(6)
    validcode = ocr.classification(img)
    print(validcode)
    return validcode

def testInternet() -> bool:
    ret = os.system("ping baidu.com -n 1")
    return True if ret == 0 else False


def main():
    if(testInternet() == True):
        print("Internet Connected")
        exit(0)
    else:
        connection_flag = False
        attempt_count = 0
        while((not connection_flag) and (attempt_count < max_attempt)):
            if(AcquireInternet(getValidCode()) == True):
                connection_flag = True
            else:
                print("Attempt {0} Fail. Try again later!".format(attempt_count+1))
                time.sleep(60)
        else:
            if(connection_flag == False):
                print("Fail to connect Internet after {0} times attempts.".format(max_attempt))
                exit(-1)
            else:
                print("Internet Connected")
                exit(0)


if __name__ == '__main__':
    if(os.path.exists('config.ini')):
        username, password, u_ip = get_user_config()
    
    if(not username or not password or not u_ip):
        print("首次使用，请配置用户名、密码和本机IP地址：")
        username = input("用户名: ")
        password = input("密码: ")
        u_ip = input("(提示：可以从认证网页中的uaddress参数找到本机IP地址)IP地址: ")
        set_user_config(username, password, u_ip)
    
    main()
