import requests
from HTMLParser import HTMLParser
requests.packages.urllib3.disable_warnings()

h = HTMLParser()

banner = '''=======================================
*       _ ___ _______         __  __  *
*      | |__ \__   __|       |  \/  | *
*      | |  ) | | | ___  __ _| \  / | *
*  _   | | / /  | |/ _ \/ _` | |\/| | *
* | |__| |/ /_  | |  __/ (_| | |  | | *
*  \____/|____| |_|\___|\__,_|_|  |_| *
*                                     *
=======================================
'''

s1 = u'ÀÁÂÃÈÉÊÌÍÒÓÔÕÙÚÝàáâãèéêìíòóôõùúýĂăĐđĨĩŨũƠơƯưẠạẢảẤấẦầẨẩẪẫẬậẮắẰằẲẳẴẵẶặẸẹẺẻẼẽẾếỀềỂểỄễỆệỈỉỊịỌọỎỏỐốỒồỔổỖỗỘộỚớỜờỞởỠỡỢợỤụỦủỨứỪừỬửỮữỰựỲỳỴỵỶỷỸỹ'
s0 = u'AAAAEEEIIOOOOUUYaaaaeeeiioooouuyAaDdIiUuOoUuAaAaAaAaAaAaAaAaAaAaAaAaEeEeEeEeEeEeEeEeIiIiOoOoOoOoOoOoOoOoOoOoOoOoUuUuUuUuUuUuUuYyYyYyYy'

def remove_accents(input_str):
    s = ''
    for c in input_str:
        if c in s1:
            s += s0[s1.index(c)]
        else:
            s += c
    return s

def login(username, password):
    return requests.post('https://apivtp.vietteltelecom.vn:6768/myviettel.php/loginV2', {'username': username, 'password': password}, verify=False).json()

def getAuthKeyVQMM(token):
    return requests.post('https://apivtp.vietteltelecom.vn:6768/myviettel.php/authVqmm', data = {'token': token, 'game_id': 'VQMM'}, verify=False).json()

def quayTay(rolling_token):
    return session.get('https://viettel.vn/4gvuitet/vong-quay?token='+rolling_token, verify=False).json()

if __name__ == "__main__":
    print banner
    
    print 'Running'

    f = open('accounts.txt').read().strip().split('\n')
    if not f or not len(f):
        print 'Please add more account into accounts.txt'
    else:
        for l in f:
            try:
                f1 = open('logs.txt', 'a')
                
                number, password = l.split('|')

                print number + '|' + 'Fetching session'
                f1.write(number + '|' + 'Fetching session' + '\n')
                
                session = requests.session()
                r = session.get('https://viettel.vn/4gvuitet', verify=False)
                raw_cookies = r.text.split('document.cookie="')[1].split('"')[0]
                cj = requests.utils.cookiejar_from_dict(dict(p.split('=') for p in raw_cookies.split('; ')))
                session.cookies = cj
                
                info = login(number, password)
                if info['errorCode'] == '0':
                    print number + '|' + 'Login success'
                    f1.write(number + '|' + 'Login success' + '\n')
                    
                    auth = getAuthKeyVQMM(info['data']['data']['token'])
                    number = info['data']['data']['phone_number']
                    if auth['errorCode'] == 0:
                        auth_key = auth['data']['auth_key']
                        print number + '|' + 'Get auth key success'
                        f1.write(number + '|' + 'Get auth key success' + '\n')
                        
                        sess = session.get('http://viettel.vn/4gvuitet?auth_key='+auth_key, verify=False)
                        html = sess.text
                        
                        if (sess.status_code != 500):                        
                            rolling_token = html.split('id="my_token" value="')[1].split('"')[0]
                            status = 1
                            while status != -1:
                                result = quayTay(rolling_token)
                                status = result['result']
                                rolling_token = result['token']
                                print number + '|' + remove_accents(h.unescape(result['message']))
                                f1.write(number + '|' + remove_accents(result['message']) + '\n')
                        else:
                            print number + '|' + 'Your account is not eligible for this promotion'
                            f1.write(number + '|' + 'Your account is not eligible for this promotion')
                            
                    else:
                        print number + '|' + 'Get auth key failed'
                        f1.write(number + '|' + 'Get auth key failed' + '\n')
                else:
                    print number + '|' + 'Login failed'
                    f1.write(number + '|' + 'Login failed' + '\n')
                    
                f1.write('\n')
                f1.close()
            except Exception as e:
                print 'An unexpected error has occured, please contact developer. Logs saved to logs.txt'
                f1.write(str(e) + '\n')
                f1.write(html + '\n')
                f1.close()
                continue

    raw_input('Script stopped, press any key to terminate...')