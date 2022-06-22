from tokens import *
import os
import sys
import time
from lib import utilities
from lib.core import Tokenizer
from requests.auth import HTTPBasicAuth
from lib.utilities import url_to_json
import multiprocessing
from attributes.continuous_integration.discoverer import CiDiscoverer
from time import strptime
from datetime import datetime
from datetime import date
from bs4 import BeautifulSoup
import requests
import arrow
import os as inner_os
from attributes.unit_test.discoverer import get_test_discoverer
import sqlite3
LICENSE_PATTERNS = [
    'http://unlicense.org/',                           # The Unlicense
    'http://mozilla.org/MPL',                          # Mozilla Public License
    'The MIT License (MIT)',                           # The MIT License
    'GNU LESSER GENERAL PUBLIC LICENSE',               # GNU LGPL
    (
        'THE SOFTWARE IS PROVIDED \"AS IS\" AND THE '
        'AUTHOR DISCLAIMS ALL WARRANTIES'
    ),                                                 # ISC
    'GNU GENERAL PUBLIC LICENSE',                      # GNU GPL
    'Eclipse Public License',                          # Eclipse Public License
    (
        'THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT '
        'HOLDERS AND CONTRIBUTORS \"AS IS\"'
    ),                                                 # BSD 3- and 2-clause
    'Artistic License',                                # Artistic License
    'http://www.apache.org/licenses',                  # Apache License
    'GNU AFFERO GENERAL PUBLIC LICENSE',               # GNU AGPL
]

from subprocess import Popen, PIPE
def _retry_if_exception(exception):
    return isinstance(exception, Exception)
def community():
    try:
        num_core_contributors = 0
        num_commits = 0
        commitList = []
        os.chdir(root_directory)
        os.chdir("path/"+repo_id+"/")
        stream = []
        for repos in os.listdir():
            if(repos == repoName):
                os.chdir(repos)
                with Popen(r'git log --pretty="%ae" | sort',shell=True,
                    stdout=PIPE, stderr=PIPE) as p:
                    output, errors = p.communicate()
                stream = output.decode('utf-8-sig',errors='ignore').splitlines()
                unique_words = set(stream)
                for words in unique_words :
                    stream.count(words)
                    commitList.append(int(stream.count(words)))
                    num_commits += int(stream.count(words))
                break
        commitList.sort(reverse=True)
        cutoff = 0.8
        aggregate = 0
        for v in commitList:
            num_core_contributors += 1
            aggregate += v
            if (aggregate / num_commits) >= cutoff:
                break
        if(num_core_contributors > 0):
            os.chdir(root_directory)
            val = (str(num_core_contributors),repo_id)
            QUERY = '''UPDATE `repoquester_results` SET `community`=? WHERE `repo_id`=?'''
            try:
                os.chdir(root_directory)
                conn = sqlite3.connect('repo_quester.db',timeout=180)
                conn.execute(QUERY,val)
                conn.commit()
                print("COMMUNITY: ",num_core_contributors)
                conn.close()
            except Exception as ex:
                print(ex)
                os.chdir(root_directory)
                conn = sqlite3.connect('repo_quester.db',timeout=180)
                conn.execute(QUERY,val)
                conn.commit()
                print("COMMUNITY: ",num_core_contributors,' trying again.. ok')
                conn.close()
    except Exception as ex:
        print(ex)

def ci():
    os.chdir(root_directory)
    ci_discoverer = CiDiscoverer()
    try:
        os.chdir(root_directory)
        result = ci_discoverer.discover(repo_path+repoName)
        if(result == True):
            val = (str(int(result)),repo_id)
            QUERY = '''UPDATE `repoquester_results` SET `continuous_integration`=? WHERE `repo_id`=?'''
            try:
                os.chdir(root_directory)
                conn = sqlite3.connect('repo_quester.db',timeout=180)
                conn.execute(QUERY,val)
                conn.commit()
                print('CI: ',result)
                conn.close()
            except Exception as ex:
                print(ex)
                os.chdir(root_directory)
                conn = sqlite3.connect('repo_quester.db',timeout=180)
                conn.execute(QUERY,val)
                conn.commit()
                print('CI: ',result,' >> trying again.. ok')
                conn.close()
    except Exception as ex:
        print(ex)
def doc():
    try:
        os.chdir(root_directory)
        ratio = 0
        util = utilities.get_loc(repo_path)
        sloc = 0
        cloc = 0
        for lang, metrics in util.items():
            sloc += metrics['sloc']
            cloc += metrics['cloc']
        if sloc == 0:
            print('DOCUMENTATION,SIZE: ',ratio)
        else:
            t_loc = sloc + cloc
            ratio = (cloc / t_loc) if t_loc > 0 else 0
            if(ratio > 0.0):
                val = (str(ratio),repo_id)
                QUERY = '''UPDATE `repoquester_results` SET `documentation`=? WHERE `repo_id`=?'''
                try:
                    os.chdir(root_directory)
                    conn = sqlite3.connect('repo_quester.db',timeout=180)
                    conn.execute(QUERY,val)
                    conn.commit()
                    conn.close()
                    print('DOCUMENTATION: ',ratio)
                except Exception as ex:
                    print(ex)
                    os.chdir(root_directory)
                    conn = sqlite3.connect('repo_quester.db',timeout=180)
                    conn.execute(QUERY,val)
                    conn.commit()
                    conn.close()
                    print('DOCUMENTATION: ',ratio,' trying again.. ok')
            if(sloc > 0):
                val2 = (str(sloc),repo_id)
                QUERY2 = '''UPDATE `repoquester_results` SET `size`=? WHERE `repo_id`=?'''
                try:
                    os.chdir(root_directory)
                    conn2 = sqlite3.connect('repo_quester.db',timeout=180)
                    conn2.execute(QUERY2,val2)
                    conn2.commit()
                    conn2.close()
                    print('SIZE: ',str(sloc))
                except Exception as ex:
                    os.chdir(root_directory)
                    conn2 = sqlite3.connect('repo_quester.db',timeout=180)
                    conn2.execute(QUERY2,val2)
                    conn2.commit()
                    conn2.close()
                    print('SIZE: ',str(sloc),' trying again.. ok')
    except Exception as ex:
        print(ex)
def history():
    avg_commits = 0
    #state = 'dormant'
    try:
        num_commits = 0
        commitList = []
        os.chdir(root_directory)
        os.chdir("path/"+repo_id+"/")
        for repos in os.listdir():
            if(repos == repoName):
                os.chdir(repos)
                stream = inner_os.popen('git log --pretty=format:"%cd"').read().split("\n")
                num_commits = len(stream)
                numberOfMonths = -1
                if(num_commits > 1):
                    prev = stream[num_commits-1].split(" ")
                    Y1 = int(prev[4])
                    M1 = int(strptime(prev[1],'%b').tm_mon)
                    D1 = int(prev[2])
                    start = datetime(Y1,M1,D1)
                    prev = stream[0].split(" ")
                    Y1 = int(prev[4])
                    M1 = int(strptime(prev[1],'%b').tm_mon)
                    D1 = int(prev[2])
                    end = datetime(Y1,M1,D1)
                    for d in arrow.Arrow.range('month', start, end):
                        numberOfMonths += 1
                    if(numberOfMonths != 0):
                        avg_commits = float(num_commits)/(float(numberOfMonths)*1.0)
                        os.chdir(root_directory)
                break
        if(avg_commits > 0.0):
            val = (str(avg_commits),repo_id)
            QUERY = '''UPDATE `repoquester_results` SET `history`=? WHERE `repo_id`=?'''
            try:
                os.chdir(root_directory)
                conn = sqlite3.connect('repo_quester.db',timeout=180)
                conn.execute(QUERY,val)
                conn.commit()
                conn.close()
                print('HISTORY: ',avg_commits)
            except Exception as ex:
                print(ex)
                os.chdir(root_directory)
                conn = sqlite3.connect('repo_quester.db',timeout=180)
                conn.execute(QUERY,val)
                conn.commit()
                conn.close()
                print('HISTORY: ',avg_commits,' trying again.. ok')
    except Exception as ex:
        print(ex)
def license():
    os.chdir(root_directory)
    json_response = {'license': False}
    try:
        flag = False
        for token in git_tokens:
            if(flag == True):
                break
            else:
                try:
                    json_response = url_to_json(URL, headers={
                            'Accept': 'application/vnd.github.drax-preview+json'
                        }
                    )
                    flag = True
                    break
                except:
                    continue
        if(flag == False):
            try:
                print("[Reg: License]Tokens didn't work! Trying out without token...")
                json_response = url_to_json(URL, headers={
                                'Accept': 'application/vnd.github.drax-preview+json'
                            }, authentication=[]
                        )
                print('Fetch ok')
            except:
                print("[Reg: License]Couldn't fetch data from API! Trying out search for patterns in the license files..")
        result = True if 'license' in json_response \
                         and json_response['license'] else False
        if not result:
            for pattern in LICENSE_PATTERNS:
                if utilities.search(pattern, repo_path, ignorecase=True):
                    result = True
                    break
        if(result == True):
            val = (str(int(result)),repo_id)
            QUERY = '''UPDATE `repoquester_results` SET `license`=? WHERE `repo_id`=?'''
            try:
                os.chdir(root_directory)
                conn = sqlite3.connect('repo_quester.db',timeout=180)
                conn.execute(QUERY,val)
                conn.commit()
                conn.close()
                print('LICENSE: ',result)
            except Exception as ex:
                print(ex)
                os.chdir(root_directory)
                conn = sqlite3.connect('repo_quester.db',timeout=180)
                conn.execute(QUERY,val)
                conn.commit()
                conn.close()
                print('LICENSE: ',result,' trying again.. ok')
    except Exception as ex:
        print(ex)
def management():
    os.chdir(root_directory)
    openIssues = 0
    closedIssues = 0
    avg_issues = 0
    try:
        numberOfMonths = 0
        totalNoOfIssues = 0
        open_url = URL.replace("api.","").replace("repos/","") + "/issues?q=is%3Aopen+is%3Aissue"
        closed_url = URL.replace("api.","").replace("repos/","") + "/issues?q=is%3Aissue+is%3Aclosed"
        flag1 = False
        for token in git_tokens:
            if(flag1 == True):
                break
            else:
                try:
                    r = requests.get(open_url, auth = HTTPBasicAuth(git_tokens[token], token))
                    dom = BeautifulSoup(r.content,'html5lib')
                    openIssues = int(dom.body.find_all('a',class_='btn-link selected')[0].text.replace("\n","").split("Open")[0])
                    flag1 = True
                    break
                except:
                    continue
        if(flag1 == False):
            try:
                r = requests.get(open_url)
                dom = BeautifulSoup(r.content,'html5lib')
                openIssues = int(dom.body.find_all('a',class_='btn-link selected')[0].text.replace("\n","").split("Open")[0])
                print('without token - open issues - fetch ok')
            except:
                openIssues = 0
        flag2 = False
        for token in git_tokens:
            if(flag2 == True):
                break
            else:
                try:
                    r = requests.get(closed_url, auth = HTTPBasicAuth(git_tokens[token], token))
                    dom = BeautifulSoup(r.content,'html5lib')
                    closedIssues = int(dom.body.find_all('a',class_='btn-link selected')[0].text.replace("\n","").split("Closed")[0])
                    flag2 = True
                    break
                except:
                    continue
        if(flag2 == False):
            try:
                r = requests.get(closed_url)
                dom = BeautifulSoup(r.content,'html5lib')
                closedIssues = int(dom.body.find_all('a',class_='btn-link selected')[0].text.replace("\n","").split("Closed")[0])
                print('without token - closed issues - fetch ok')
            except:
                closedIssues = 0
        totalNoOfIssues  = openIssues + closedIssues
        num_commits = 0
        os.chdir("path/"+repo_id+"/")
        for repos in os.listdir():
            if(repos == repoName):
                os.chdir(repos)
                stream = inner_os.popen('git log --pretty=format:"%cd"').read().split("\n")
                num_commits = len(stream)
                numberOfMonths = -1
                if(num_commits > 1):
                    prev = stream[num_commits-1].split(" ")
                    Y1 = int(prev[4])
                    M1 = int(strptime(prev[1],'%b').tm_mon)
                    D1 = int(prev[2])
                    start = datetime(Y1,M1,D1)
                    prev = stream[0].split(" ")
                    Y1 = int(prev[4])
                    M1 = int(strptime(prev[1],'%b').tm_mon)
                    D1 = int(prev[2])
                    end = datetime(Y1,M1,D1)
                    for d in arrow.Arrow.range('month', start, end):
                        numberOfMonths += 1
                issueFrequency = 0
                break
        if numberOfMonths >= 1:
            avg_issues = totalNoOfIssues / numberOfMonths*1.0
            if(avg_issues > 0.0):
                val = (str(avg_issues),repo_id)
                QUERY = '''UPDATE `repoquester_results` SET `management`=? WHERE `repo_id`=?'''
                try:
                    os.chdir(root_directory)
                    conn = sqlite3.connect('repo_quester.db',timeout=180)
                    conn.execute(QUERY,val)
                    conn.commit()
                    conn.close()
                    print('ISSUES: ',avg_issues)
                except Exception as ex:
                    print(ex)
                    os.chdir(root_directory)
                    conn = sqlite3.connect('repo_quester.db',timeout=180)
                    conn.execute(QUERY,val)
                    conn.commit()
                    conn.close()
                    print('ISSUES: ',avg_issues,' trying again.. ok')
    except Exception as ex:
        print(ex)
def unit_test():
    proportion = 0.0
    lang = ""
    for x in range(3,arg_len-1):
        lang += str(sys.argv[x])
    flag1 = False
    if(lang == 'NULL'):
        for token in git_tokens:
            if(flag1 == True):
                break
            else:
                try:
                    lang = requests.get(URL, auth = HTTPBasicAuth(git_tokens[token], token)).json()['language']
                    flag1 = True
                    break
                except:
                    continue
        if(flag1 == False):
            try:
                lang = requests.get(URL).json()['language']
                print('without token - language - fetch ok')
            except Exception as ex:
                print(ex)
    os.chdir(root_directory)
    repo_path_abs = str(os.getcwd()) + "/" +repo_path
    try:
        try:
            discoverer = get_test_discoverer(language=lang)
            proportion = discoverer.discover(repo_path_abs)
        except Exception as ex:
            print(ex)
            print('Failed to get Unit Test Value...')
            proportion = 0.0
        if(proportion > 0.0):
            val = (str(proportion),repo_id)
            QUERY = '''UPDATE `repoquester_results` SET `unit_test`=? WHERE `repo_id`=?'''
            try:
                os.chdir(root_directory)
                conn = sqlite3.connect('repo_quester.db',timeout=180)
                conn.execute(QUERY,val)
                conn.commit()
                conn.close()
                print('UNIT_TEST: ',proportion,' ok')
            except Exception as ex:
                print(ex)
                os.chdir(root_directory)
                conn = sqlite3.connect('repo_quester.db',timeout=180)
                conn.execute(QUERY,val)
                conn.commit()
                conn.close()
                print('UNIT_TEST: ',proportion,' trying again.. ok')
    except Exception as ex:
        print(ex)

def prs():
    os.chdir(root_directory)
    mpr = 0
    cpr = 0
    opr = 0
    try:
        pr_rate = 0
        url =  URL.replace("api.","").replace("repos/","")
        urlList = ["/pulls","/pulls?q=is%3Apr+is%3Aclosed+","/pulls?q=is%3Apr+is%3Amerged+"]
        url_opr = url+urlList[0]
        url_cpr = url+urlList[1]
        url_mpr = url+urlList[2]
        flag1 = False
        for token in git_tokens:
            if(flag1 == True):
                break
            else:
                try:
                    r = requests.get(url_opr, auth = HTTPBasicAuth(git_tokens[token], token))
                    dom = BeautifulSoup(r.content,'html5lib')
                    opr  = int(dom.body.find_all('a',class_='btn-link selected')[0].text.replace("\n","").split("Open")[0])
                    flag1 = True
                    break
                except:
                    continue
        if(flag1 == False):
            try:
                r = requests.get(url_opr)
                dom = BeautifulSoup(r.content,'html5lib')
                opr  = int(dom.body.find_all('a',class_='btn-link selected')[0].text.replace("\n","").split("Open")[0])
                print('without token - closed issues - fetch ok')
            except:
                opr = 0
        flag2 = False
        for token in git_tokens:
            if(flag2 == True):
                break
            else:
                try:
                    r = requests.get(url_cpr, auth = HTTPBasicAuth(git_tokens[token], token))
                    dom = BeautifulSoup(r.content,'html5lib')
                    cpr  = int(dom.body.find_all('a',class_='btn-link selected')[0].text.replace("\n","").split("Closed")[0])
                    flag2 = True
                    break
                except:
                    continue
        if(flag2 == False):
            try:
                r = requests.get(url_cpr)
                dom = BeautifulSoup(r.content,'html5lib')
                cpr  = int(dom.body.find_all('a',class_='btn-link selected')[0].text.replace("\n","").split("Closed")[0])
            except:
                cpr = 0
        flag3 = False
        for token in git_tokens:
            if(flag3 == True):
                break
            else:
                try:
                    r = requests.get(url_mpr, auth = HTTPBasicAuth(git_tokens[token], token))
                    dom = BeautifulSoup(r.content,'html5lib')
                    mpr  = int(dom.body.find_all('a',class_='btn-link selected')[0].text.replace("\n","").split("Total")[0])
                    flag3 = True
                    break
                except:
                    continue
        if(flag3 == False):
            try:
                r = requests.get(url_mpr)
                dom = BeautifulSoup(r.content,'html5lib')
                mpr  = int(dom.body.find_all('a',class_='btn-link selected')[0].text.replace("\n","").split("Total")[0])
            except:
                mpr = 0
        pr = mpr+cpr+opr
        if(pr > 0):
            pr_rate = float(mpr+cpr)/float(pr*1.0)
            val = (str(pr_rate),repo_id)
            QUERY = '''UPDATE `repoquester_results` SET `pull`=? WHERE `repo_id`=?'''
            try:
                os.chdir(root_directory)
                conn = sqlite3.connect('repo_quester.db',timeout=180)
                conn.execute(QUERY,val)
                conn.commit()
                conn.close()
                print("PR rate: ",pr_rate)
            except Exception as ex:
                os.chdir(root_directory)
                conn = sqlite3.connect('repo_quester.db',timeout=180)
                conn.execute(QUERY,val)
                conn.commit()
                conn.close()
                print("PR rate: ",pr_rate,' trying again.. ok')
    except Exception as ex:
        print(ex)

def time_gap(time2,time1):
    Y1 = int(time1[4])
    M1 = int(strptime(time1[1],'%b').tm_mon)
    D1 = int(time1[2])
    end = datetime(Y1,M1,D1)
    Y2 = int(time2[4])
    M2 = int(strptime(time2[1],'%b').tm_mon)
    D2 = int(time2[2])
    start = datetime(Y2,M2,D2)
    numberOfDays = -1
    for d in arrow.Arrow.range('day', start, end):
        numberOfDays += 1
    return numberOfDays

def releases():
    release_score = 0
    try:
        os.chdir(root_directory)
        os.chdir("path/"+str(repo_id)+"/")
        for repos in os.listdir():
            if(repos == repoName):
                os.chdir(repos)
                stream = inner_os.popen('git for-each-ref --format="%(refname:short) | %(creatordate)" refs/tags/* --sort=creatordate').read().split("\n")
                totalNumberOfReleases = 0
                today = datetime.today().date()
                if isinstance(today, str):
                    today = datetime.strptime(today, '%Y-%m-%d')
                if(len(stream) > 3 ):
                    if(len(stream)-2 > 0):
                        time1 = stream[len(stream)-2].split("| ")[1].split(" ") # Latest release date
                        Y1 = int(time1[4])
                        M1 = int(strptime(time1[1],'%b').tm_mon)
                        D1 = int(time1[2])
                        end = datetime(Y1,M1,D1)
                        time2 = stream[0].split("| ")[1].split(" ") # First release date
                        Y2 = int(time2[4])
                        M2 = int(strptime(time2[1],'%b').tm_mon)
                        D2 = int(time2[2])
                        start = datetime(Y2,M2,D2)
                        numberOfDays = -1
                        for d in arrow.Arrow.range('day', start, end):
                            numberOfDays += 1
                        totalNumberOfReleases = len(stream)-1
                        averageReleaseTime = numberOfDays/totalNumberOfReleases # In number of days
                        timeNow = str(today).split(" ")[0].split("-")
                        Y2 = int(timeNow[0])
                        M2 = int(timeNow[1])
                        D2 = int(timeNow[2])
                        now = datetime(Y1,M2,D2)
                        daysPassed = -1
                        for d in arrow.Arrow.range('day',end,now):
                            daysPassed += 1
                        if(daysPassed <= averageReleaseTime):
                            release_score = 1
                        break
        if(release_score > 0):
            os.chdir(root_directory)
            val = (str(release_score),repo_id)
            QUERY = '''UPDATE `repoquester_results` SET `releases`=? WHERE `repo_id`=?'''
            try:
                os.chdir(root_directory)
                conn = sqlite3.connect('repo_quester.db',timeout=180)
                conn.execute(QUERY,val)
                conn.commit()
                conn.close()
                print("RELEASE SCORE: ",release_score)
            except Exception as ex:
                print(ex)
                os.chdir(root_directory)
                conn = sqlite3.connect('repo_quester.db',timeout=180)
                conn.execute(QUERY,val)
                conn.commit()
                conn.close()
                print("RELEASE SCORE: ",release_score,' trying again.. ok')
    except Exception as ex:
        print(ex)

arg_len = len(sys.argv)
repo_id = str(sys.argv[1])
URL = str(sys.argv[2])
lang = ""
for x in range(3,arg_len-1):
    lang += str(sys.argv[x])
repoName = str(sys.argv[arg_len-1])
repo_path = "path/" + repo_id + "/"
def main():
    processes = []
    p = multiprocessing.Process(target=community,args=())
    processes.append(p)
    p.start()
    p = multiprocessing.Process(target=ci,args=())
    processes.append(p)
    p.start()
    p = multiprocessing.Process(target=doc,args=())
    processes.append(p)
    p.start()
    p = multiprocessing.Process(target=history,args=())
    processes.append(p)
    p.start()
    p = multiprocessing.Process(target=license,args=())
    processes.append(p)
    p.start()
    p = multiprocessing.Process(target=management,args=())
    processes.append(p)
    p.start()
    p = multiprocessing.Process(target=unit_test,args=())
    processes.append(p)
    p.start()
    p = multiprocessing.Process(target=prs,args=())
    processes.append(p)
    p.start()
    p = multiprocessing.Process(target=releases,args=())
    processes.append(p)
    p.start()
    for process in processes:
        process.join()
if __name__ == "__main__":
    starttime = time.time()
    main()
    print('Total time {} seconds'.format(time.time()-starttime))
