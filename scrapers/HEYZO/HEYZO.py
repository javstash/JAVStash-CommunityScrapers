# -*- coding: UTF-8 -*-
import sys, json, re, requests
from lxml import html
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
res = {}
code_regex = r"\b(\d{4})\b"
log(stdin['url'])
if (sys.argv[1] == "sceneByName"):
    query_code = re.search(code_regex, stdin['name']).group(1)
    query_url = "https://www.heyzo.com/moviepages/"+query_code+"/index.html"
elif (sys.argv[1] == "sceneByQueryFragment" or sys.argv[1] == "sceneByFragment"):
    try:
        query_code = re.search(code_regex, stdin['code']).group(1)
        query_url = "https://www.heyzo.com/moviepages/"+query_code+"/index.html"
    except:
        query_code = re.search(code_regex, stdin['url']).group(1)
        query_url = stdin['url']
elif (sys.argv[1] == "sceneByURL"):
    query_code = re.search(code_regex, stdin['url']).group(1)
    query_url = stdin['url']

query_url = "https://www.heyzo.com/moviepages/"+query_code+"/index.html"
log(query_url)
r = requests.get(query_url)

parsed_content = html.fromstring(r.content)

date_xpath = '//div[@class="info-bg"]/table/tbody/tr/td[contains(.,"公開日")]/following-sibling::td/text()|//span[@class="release-day"]/following-sibling::span[1]/span/text()|//span[@class="release-day"]/following-sibling::span[1]/text()'
performer_xpath = '//div[@class="info-bg"]/table/tbody/tr/td[contains(.,"Actress") or contains(.,"出演")]/following-sibling::td/a/span/text()|//span[@class="actor"]/following-sibling::span[1]/a/text()|//span[@class="actor"]/following-sibling::span[1]/a/span/text()'
json_selector = '//script[@type="application/ld+json"]/text()'

try:
    json_result = json.loads(parsed_content.xpath(json_selector)[0].strip(),strict=False)
except Exception as e:
    log(e)
    log("JSON parse failed")

title = ""
date = ""
details = ""

try:
    title = json_result['name']
except:
    title = parsed_content.xpath('//div[@id="movie"]/h1/text()')[0].split()[0]

try:
    date = json_result['dateCreated'][:10]
except:
    date = date = parsed_content.xpath(date_xpath)[0].strip()

try:
    details = json_result['description']
except:
    try:
        details = parsed_content.xpath('//p[@class="memo"]')[0].text_content()
    except IndexError:
        details = ""
        log("No details found")

if ("近日公開" in date):
    date = ""

performer_list = parsed_content.xpath(performer_xpath)

tags0 = parsed_content.xpath('//tr[@class="table-actor-type"]/td/span/a/text()')
tags1 = parsed_content.xpath('//tr[@class="table-tag-keyword-small"]//ul[@class="tag-keyword-list"]/li/a/text()')

tags = tags0+tags1

res['title']=title
res['details']=details
res["performers"] = [{'name': i} for i in performer_list]
res["tags"] = [{'name': i} for i in tags]
res["date"] = date
res["url"] = query_url
res["code"] = 'HEYZO-'+query_code
res["image"] = "https://www.heyzo.com/contents/3000/"+query_code+"/images/player_thumbnail.jpg"

log(json.dumps([res],ensure_ascii=ensure_ascii))

if (sys.argv[1] == "sceneByName"):
    print(json.dumps([res],ensure_ascii=ensure_ascii)) 
else:
    print(json.dumps(res,ensure_ascii=ensure_ascii)) 


