import sqlite3
fp = open('repo_ids','r')
ids = []
for id in fp:
    ids.append(id.replace("\n",""))
fp.close()
fp = open('repo_urls','r')
urls = []
for id in fp:
    urls.append(id.replace("\n",""))
fp.close()
fp = open('repo_languages','r')
langs = []
for id in fp:
    langs.append(id.replace("\n",""))
fp.close()
conn = sqlite3.connect('repo_quester.db')
for x in range(len(ids)):
    val = (int(ids[x]),urls[x],langs[x],'0','0','0','0','0','0','0','0','0','0')
    QUERY = '''
    INSERT INTO `repoquester_results`
    (`repo_id`,`repository`,`language`,`community`,`continuous_integration` ,`documentation`,`history` ,`management`,`license` ,`unit_test`,`pull` ,`releases`,`size`)
    VALUES
    (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)'''
    conn.execute(QUERY,val)

conn.commit()
print("Table repoquester is ready!")
conn.close()
