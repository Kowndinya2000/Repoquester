[![DOI](https://zenodo.org/badge/506275894.svg)](https://zenodo.org/badge/latestdoi/506275894)

# RepoQuester (version 0.0.1)

## What is RepoQuester?
RepoQuester is a command-line tool to assist developers in evaluating projects by providing quantitative scores for ten metrics that span project collaboration, quality and maintenance. 

## RepoQuester Overview 
We implemented RepoQuester by forking and modifying the Repo Reaper tool.
Reaper needs the GHTorrent database's queryable offline mirror which contains information about millions of GitHub repositories. To run the Reaper tool, users have to initially download the database offline mirror~(more than 100GB) onto their local machines.
Reaper then queries the SQL tables in the GHTorrent database for obtaining meta-information about a repository.
To update the Reaper's dataset one has to re-download the GHTorrent's latest dump and reanalyze the repositories.
Reaper analyzes a project by calculating values for eight metrics which involves joining various SQL tables in GHTorrent.
RepoQuester however does not rely on GHTorrent. 

## Advantage of using RepoQuester
Unlike RepoReaper, the RepoQuester can be used on a local machine to analyze any number of projects by providing the project's URL and programming language as input either on the command line or inside a configuration file.
Below here is the architecture of RepoQuester
![Image](https://github.com/Kowndinya2000/repoquester/blob/master/Architecture.png)

## Use case scenarios for RepoQuester
We bring forward a few use case scenarios where RepoQuester can be used. Consider the following four scenarios where one would want a good quality project:

1) Consider Arjun, an undergraduate who wanted to build a small customized Java Script framework for his project. He found a set of GitHub projects to fork and customize. He needed to select one project among them; he needed to understand whether a project is well-documented and well-tested and whether the project's library dependencies are upgraded to the latest.

2) Chaitra, a software developer, wants to contribute to open-source projects with an active community around them, licensed, and using continuous integration services. 

3) Consider Jay, a graduate working on evaluating a set of Ruby projects on GitHub to utilize them as libraries. He might want to know whether the library is active or deprecated, well-tested, and less prone to issues.  

5) Dhruva and their team are building an open-source cryptocurrency project. They wanted to follow best practices during the project's development, such as writing test files, writing code comments, implementing continuous integration services, and so on; however, they are finding it difficult to assess whether their project has improved over time. Their goal is to keep track of different project dimensions that can improve their project usability and maintenance. 

As described in the above four scenarios, developers often need to evaluate which project on GitHub to interact with, and not all relevant information is readily available. And RepoQuester can help automate the process of mining GitHub projects by providing scores for metrics (that span project collaboration, quality, and maintenance) for the projects being considered.  


## Future Work
In order to improve our tool, we wish to collect developer feedback on RepoQuester's metrics through surveys. Metrics such as "Pull Requests Ratio", "Releases", "Continuous Integration" could be coupled with statistical analysis and more advanced methods in order to derive more insights. Using RepoQuester at the core, individual developers/researchers can build recommender systems to suggest projects to users for search categories such as library reuse, documentation quality, community support, ownership and licensing of a repository, continuous integration services, release frequency, library re-implementation and so on 

# Steps to install the tool
> Download this GitHub repository onto your local machine 
````
git clone https://github.com/Kowndinya2000/Repoquester
````

# Steps to install the dependencies
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

# Steps to run the tool RepoQuester
> 1. Open the file ```repo_urls``` 
````
Add username/repositoryname in newlines. 
A sample of 265 repository urls are present already in the file.
````
> 2. Open the file ```tokens.py``` 
````
Alteast provide one Github Personal Access Token. 
Format to provide token can be viewed in the file.
````
> 3. Initialize the database
````
chmod +x *sh
sed -i -e 's/\r$//' initialize.sh
./initialize.sh
````
> 4. Run the script to analyze the repositories
````
./run.sh
````
> 5. Check the results in the database file ```repo_quester.db```

> 6. To re-run the analysis without modyfing repository information
````
chmod +x *sh
./clean.sh
./run.sh
````
> 7. To empty the repository information and results.
````
chmod +x *sh
./empty.sh
(This also deletes the database file. Only retains the usable tool template)
Follow the steps 1-4 again.  
````
> 8. To run a particular repository.
````
For example, to analyze repository with repo_id = 2 : run the below two commands
chmod +x script2.sh
./script2.sh
````
## Commands to query the database (refer to file connect.py to refer to schema)
> Open the file ```repo_quester.db``` 
>> Database file could be viewed in DB Browser for SQLite (download link: https://sqlitebrowser.org/)
>>> Table: ```repoquester_results```

> 9. To select a repository "Microsoft/IEDiagnosticsAdapter" use the below command: 
````
SELECT * FROM repoquester_results WHERE repository in ("Microsoft/IEDiagnosticsAdapter");
````
![Command Cell](https://kowndinya2000.github.io/repo-quester-resources.github.io/sql_command_cell.png)

> 10. To select a set of metrics for the repository "Microsoft/IEDiagnosticsAdapter" 
>> For example, to select metrics: community, continuous_integration and license use the below command:
````
SELECT community,continuous_integration,license FROM repoquester_results WHERE repository in ("Microsoft/IEDiagnosticsAdapter");
````
> 11. The results table can be exported to ```CSV```, ```JSON``` and ```sql``` file formats 
````
In the DB Browser for SQLite application:
Click on File->Export-> Database to SQL file
                     -> Table(s) as CSV file
                     -> Table(s) to JSON
````
![Export Results](https://kowndinya2000.github.io/repo-quester-resources.github.io/export2.png)

# Demonstration video of our tool
Please find a demo video [here](https://youtu.be/Q8OdmNzUfN0) 


# How to Contact?
For more information about the project and support requests, feel free to contact Kowndinya Boyalakuntla (cs17b032@iittp.ac.in). Please open an issue or pull request if you find any bug or have an idea for enhancement. 

