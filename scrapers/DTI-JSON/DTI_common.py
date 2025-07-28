# -*- coding: UTF-8 -*-
import sys, json, re, requests
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

def log(*s):
    print(*s, file=sys.stderr)

if(sys.platform=='win32'):
    ensure_ascii=True
else:
    ensure_ascii=False

# Set Language
LANG='JA' # JA or EN

stdin = json.loads(sys.stdin.read())
studio = sys.argv[1]
res = {}

with open('index.json', 'r') as file:
    index = json.load(file)
    json_prefix = index[studio]['json_prefix']
    url_prefix = index[studio]['url_prefix']
    code_regex = fr"{index[studio]['code_regex']}"
    res["studio"] = {"name": index[studio]['studio_name']}

if (sys.argv[2] == "sceneByName"):
    query_string = re.search(code_regex, stdin['name']).group(1)
elif (sys.argv[2] == "sceneByQueryFragment" or sys.argv[2] == "sceneByFragment"):
    try:
        query_string = re.search(code_regex, stdin['code']).group(1)
    except:
        query_string = re.search(code_regex, stdin['url']).group(1)
elif (sys.argv[2] == "sceneByURL"):
    query_string = re.search(code_regex, stdin['url']).group(1)

json_url = json_prefix+"movie_details/movie_id/"+query_string+".json"
log(json_url)
r = requests.get(json_url)

r_json = r.json()

if LANG == "JA":
    res['title']=r_json['Title']
    res['details']=r_json['Desc']
    res["performers"] = [{'name': i} for i in r_json['ActressesJa']]
    res["tags"] = [{'name': i} for i in r_json['UCNAME']]


if LANG == "EN":
    res['title']=r_json['TitleEn']
    res['details']=r_json['DescEn']
    res["performers"] = [{'name': i} for i in r_json['ActressesEn']]
    res["tags"] = [{'name': i} for i in r_json['UCNAMEEn']]

res["date"] = r_json['Release']
res["url"] = url_prefix+query_string+"/"

res["code"] = query_string+'-'+studio

image = r_json['ThumbUltra']

if (image is None and studio  == "carib"):
    image = "https://www.caribbeancom.com/moviepages/"+query_string+"/images/l_l.jpg"

if (studio == "1pon" and not (re.match(r'1pondo\.tv',image))):
    image = "https://www.1pondo.tv/moviepages/"+query_string+"/images/str.jpg"

response = requests.get(image)

#
if response.ok:
    pass
else:
    if (studio == "1pon"):
        image = "https://www.1pondo.tv/assets/sample/"+query_string+"/str.jpg"
        
    if (studio == "10mu"):
        response = requests.get("https://web.archive.org/web/https://www.10musume.com/moviepages/"+query_string+"/images/str.jpg")
        if (response.ok):
            try:
                image = response.links['memento']['url']
            except:
                pass
        else:
            response = requests.get("https://web.archive.org/web/https://www.10musume.com/moviepages/"+code_raw+"/images/d_b.jpg")
            if (response.ok):
                try:
                    image = response.links['memento']['url']
                except:
                    pass
        
res["image"] = image

log(json.dumps([res],ensure_ascii=ensure_ascii))

if (sys.argv[2] == "sceneByName"):
    print(json.dumps([res],ensure_ascii=ensure_ascii)) 
else:
    print(json.dumps(res,ensure_ascii=ensure_ascii)) 


