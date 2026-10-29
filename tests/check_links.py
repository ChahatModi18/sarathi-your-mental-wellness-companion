import re,urllib.request,ssl
p=r'c:/Users/Lenovo/python projects/.venv/Main.py'
s=open(p,encoding='utf-8').read()
urls=re.findall(r"https://www\.youtube\.com/watch\?v=[A-Za-z0-9_\-]+",s)
urls=sorted(set(urls))
print('Found',len(urls),'YouTube URLs')
ctx=ssl.create_default_context()
for u in urls:
    try:
        req=urllib.request.Request(u, method='HEAD', headers={'User-Agent':'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=10, context=ctx) as r:
            print(u, '=>', r.status)
    except Exception as e:
        print(u, '=> ERROR:', e)
