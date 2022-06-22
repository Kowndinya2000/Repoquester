from tokens import *
fp = open('repo_ids','r')
ids = []
for id in fp:
    ids.append(id.replace("\n",""))
fp.close()
fp = open('repo_urls','r')
urls = []
for id in fp:
    urls.append('https://api.github.com/repos/'+id.replace("\n",""))
fp.close()
fp = open('repo_languages','r')
lang = []
for id in fp:
    lang.append(id.replace("\n",""))
fp.close()
fp3 = open('score.sh','a')
for x in range(len(ids)):
    repo_id = ids[x]
    fp2 = open("script"+repo_id+".sh","a")
    url_a = urls[x]
    name = urls[x].split("/")[5]
    url = urls[x].replace("https://api.github.com/repos","")
    url0 = "https://github.com" + url
    for token in git_tokens:
        url_t = "https://" + token + ":x-oauth-basic@github.com" + url
        fp2.write("git clone "+ url_t +" path/"+repo_id+"/"+name +" || ")
    langs = lang[x]
    if(len(langs) == 0):
    	langs = "NULL"
    fp2.write("git clone "+ url0 +" path/"+repo_id+"/"+name  + " > logfile.txt \n")
    fp2.write("chmod +x path/"+repo_id+"\n")
    fp2.write("chmod +x path/"+repo_id+"/"+name+"\n")
    fp2.write("chmod +x path/"+repo_id+"/"+name+"/\n")
    fp2.write('wait\n')
    fp2.write('python3 main.py '+repo_id + ' ' + url_a  + ' ' + langs + ' ' + name +"\n")
    # Repository will be deleted after storing the results in the database
    # Comment the below 2 lines if you do not want to delete the downloaded repository
    fp2.write('wait\n')
    fp2.write("rm -rf path/"+repo_id+"\n")
    fp2.close()
    fp3.write("./script"+repo_id+".sh\n")
fp3.close()
