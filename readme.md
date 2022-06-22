[![DOI](https://zenodo.org/badge/506275894.svg)](https://zenodo.org/badge/latestdoi/506275894)

# RepoQuester
RepoQuester is a command-line tool to assist developers in evaluating projects by providing quantitative scores for ten metrics that span project collaboration, quality and maintenance. 

# RepoQuester Overview 
We implemented RepoQuester by forking and modifying the Repo Reaper tool.
Reaper needs the GHTorrent database's queryable offline mirror which contains information about millions of GitHub repositories. To run the Reaper tool, users have to initially download the database offline mirror~(more than 100GB) onto their local machines.
Reaper then queries the SQL tables in the GHTorrent database for obtaining meta-information about a repository.
To update the Reaper's dataset one has to re-download the GHTorrent's latest dump and reanalyze the repositories.
Reaper analyzes a project by calculating values for eight metrics which involves joining various SQL tables in GHTorrent.
RepoQuester however does not rely on GHTorrent. 
It can be used on a local machine to analyze any number of projects by providing the project's URL and programming language as input either on the command line or inside a configuration file.
Below here is the architecture of RepoQuester
![Image](https://github.com/Kowndinya2000/repoquester/blob/master/Architecture.png)
# Steps to run the tool RepoQuester
> 1. Install python libraries
````
pip install -r requirements.txt
````
> 2. Download ```cloc```
````
https://github.com/AlDanial/cloc/tree/1.88#install-via-package-manager
Example: For Debian or Ubuntu OS: sudo apt install cloc
````
> 3. Download ```Ack```
```
https://beyondgrep.com/install/
Example: For Debian or Ubuntu OS: sudo apt install ack-grep 
```
> 4. Open the file ```repo_urls``` 
````
Add username/repositoryname in newlines. 
A sample of 265 repository urls are present already in the file.
````
> 5. Open the file ```tokens.py``` 
````
Alteast provide one Github Personal Access Token. 
Format to provide token can be viewed in the file.
````
> 6. Initialize the database
````
chmod +x *sh
sed -i -e 's/\r$//' initialize.sh
./initialize.sh
````
> 7. Run the script to analyze the repositories
````
./run.sh
````
> 8. Check the results in the database file ```repo_quester.db```

> 9. To re-run the analysis without modyfing repository information
````
chmod +x *sh
./clean.sh
./run.sh
````
> 10. To empty the repository information and results.
````
chmod +x *sh
./empty.sh
(This also deletes the database file. Only retains the usable tool template)
Follow the steps 4-7 again.  
````
> 11. To run a particular repository.
````
For example, to analyze repository with repo_id = 2 : run the below two commands
chmod +x script2.sh
./script2.sh
````
## Commands to query the database (refer to file connect.py to refer to schema)
> Open the file ```repo_quester.db``` 
>> Database file could be viewed in DB Browser for SQLite (download link: https://sqlitebrowser.org/)
>>> Table: ```repoquester_results```

> 12. To select a repository "Microsoft/IEDiagnosticsAdapter" use the below command: 
````
SELECT * FROM repoquester_results WHERE repository in ("Microsoft/IEDiagnosticsAdapter");
````
![Command Cell](https://kowndinya2000.github.io/repo-quester-resources.github.io/sql_command_cell.png)

> 13. To select a set of metrics for the repository "Microsoft/IEDiagnosticsAdapter" 
>> For example, to select metrics: community, continuous_integration and license use the below command:
````
SELECT community,continuous_integration,license FROM repoquester_results WHERE repository in ("Microsoft/IEDiagnosticsAdapter");
````
> 14. The results table can be exported to ```CSV```, ```JSON``` and ```sql``` file formats 
````
In the DB Browser for SQLite application:
Click on File->Export-> Database to SQL file
                     -> Table(s) as CSV file
                     -> Table(s) to JSON
````
![Export Results](https://kowndinya2000.github.io/repo-quester-resources.github.io/export2.png)

# How to Contact?
For more information about the project and support requests, feel free to contact Kowndinya Boyalakuntla (cs17b032@iittp.ac.in). Please open an issue or pull request if you find any bug or have an idea for enhancement. 

