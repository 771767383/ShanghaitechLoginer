import os
import configparser
import requests
from bs4 import BeautifulSoup
import time
import ddddocr
import socket
import platform
import subprocess

ocr = ddddocr.DdddOcr(beta=True, show_ad = False)

max_attempt = 20
username = None
password = None
u_ip = None

ac_ip = "10.13.7.59"
pushPageId = "5bf74194-d2a8-4bb8-ac6b-8ff3e855f6a7"
ssid = "PUxzd1NzaWRQbGFjZWhvbGRlcj0="
url_prefix = "https://net-auth.shanghaitech.edu.cn:19008/portalpage/04b92f0a808c4d10b572642e3be564b2/20221024095238/pc/auth.html"

def get_refer_url():
    return url_prefix + "?ac-ip={acip}&uaddress={uip}&umac=null&authType=1&lang=zh_CN&ssid={sid}&pushPageId={pid}".format(acip=ac_ip, uip = u_ip, sid = ssid,pid = pushPageId)

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




def get_local_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        # connect to the auth server to determine the correct outgoing interface
        # This is more accurate than 8.8.8.8 for campus networks
        s.connect((ac_ip, 19008))
        local_ip = s.getsockname()[0]
        s.close()
        return local_ip
    except Exception:
        try:
            # Fallback to public DNS if auth server is unreachable
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            local_ip = s.getsockname()[0]
            s.close()
            return local_ip
        except Exception:
            return "127.0.0.1"

def testInternet(host="baidu.com") -> bool:
    param = '-n' if platform.system().lower() == 'windows' else '-c'
    # Use subprocess to hide output and support cross-platform
    try:
        command = ['ping', param, '1', host]
        return subprocess.call(command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL) == 0
    except Exception:
        return False

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
    'Referer': get_refer_url(),
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
    'Referer': get_refer_url(),
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

def main():
    local_ip = get_local_ip()
    print("Local IP: {}".format(local_ip))
    print("Target IP: {}".format(u_ip))

    is_connected = testInternet()

    should_auth = False
    if not is_connected:
        print("Internet Not Connected. Starting login process...")
        should_auth = True
    elif u_ip != local_ip:
        print("Local internet connected, but target IP ({}) differs from local IP ({}). executing auth...".format(u_ip, local_ip))
        should_auth = True
    else:
        print("Internet Connected.")
        exit(0)

    if should_auth:
        connection_flag = False
        attempt_count = 0
        while((not connection_flag) and (attempt_count < max_attempt)):
            # If we are helping a remote IP and we already have internet, 
            # AcquireInternet will return True (because testInternet() is True).
            # But the POST request inside it has been executed.
            if(AcquireInternet(getValidCode()) == True):
                connection_flag = True
            else:
                print("Attempt {0} Fail. Try again later!".format(attempt_count+1))
                time.sleep(60)
        
        if(connection_flag == False):
            print("Fail to connect Internet after {0} times attempts.".format(max_attempt))
            exit(-1)
        else:
            print("Login process completed.")
            if u_ip != local_ip:
                print("Pinging target host {} ...".format(u_ip))
                if testInternet(u_ip):
                    print("Ping {} Success.".format(u_ip))
                else:
                    print("Ping {} Failed.".format(u_ip))
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
