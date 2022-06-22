# Ensure the files repo_urls and repo_languages are committed with the list of repositories you need

fp = open('repo_ids','w')
fp.write('')
fp.close()

fp = open('repo_ids','a')
open_urls = open('repo_urls','r')
counter = 0
stream = ""
for x in open_urls:
    stream +=  str(counter) + "\n"
    counter+=  1
fp.write(stream[:len(stream)-1])
open_urls.close()
fp.close()
