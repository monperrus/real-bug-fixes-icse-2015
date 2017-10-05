This is an open-science Github repository.

It contains the bug fix commit dataset of [An Empirical Study on Real Bug Fixes (ICSE 2015)](http://stap.sjtu.edu.cn/images/8/86/Icse15-bugstudy.pdf).

* The 5 `*orig.txt` contain the SVN commit identifiers. The files were given by Hao Zhong in a private communication, expect for Cassandra, whose commit list has been reconstructed. The format of the fourth column is {commit id}_{issue id}. If the issue id is “internal”, it means that the commit has been included because the commit message uses "bug" or "fix".
* The 14914 `log.d/*` files contains the commit metadata (message, author, date)
* The 14914 `svn.d/*` files contains the files touched by the commits (the file name contains the commit identifier)
* The 5956 `jira.d/*` files contains the JSON data of the JIRA bug reports mentioned in the commit messages

The two python files create a bug JSON file called `bug-fix-commit-dataset.json` with all information merged.



