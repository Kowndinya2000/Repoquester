import sqlite3

conn = sqlite3.connect('repo_quester.db')

conn.execute('''CREATE TABLE `repoquester_results` (
  `repo_id` int(11) NOT NULL,
  `repository` varchar(255) NOT NULL,
  `language` varchar(255) NOT NULL,
  `community` double DEFAULT NULL,
  `continuous_integration` double DEFAULT NULL,
  `documentation` double DEFAULT NULL,
  `history` double DEFAULT NULL,
  `management` double DEFAULT NULL,
  `license` double DEFAULT NULL,
  `unit_test` double DEFAULT NULL,
  `pull` double DEFAULT NULL,
  `releases` double DEFAULT NULL,
  `size` double DEFAULT NULL,
  PRIMARY KEY (`repo_id`)
);''')
print("Database schema ready!")

conn.close()
