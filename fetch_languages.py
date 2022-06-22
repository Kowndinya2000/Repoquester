import requests 
from tokens import *
from requests.auth import HTTPBasicAuth
fp = open("repo_urls","r")
fp2 = open("repo_languages","w")
fp2.write("")
fp2.close()
fp2 = open("repo_languages","a")
urls_working = ""
for x in fp:
    for token in git_tokens:
        token_worked = False
        try:
            req = requests.get("https://github.com/"+x.replace("\n",""))
            if(req.status_code == 200):
                lang = requests.get("https://api.github.com/repos/"+x.replace("\n",""), auth = HTTPBasicAuth(git_tokens[token], token)).json()["language"]
                if(lang != None and lang != "" and len(lang) > 0):
                    urls_working += x
                    print(lang)
                    fp2.write(lang+"\n")
                    token_worked = True
        except:
            continue
        if(token_worked == True):
            break
fp2.close()
fp.close()

fp = open("repo_urls","w")
fp.write(urls_working)
fp.close()
