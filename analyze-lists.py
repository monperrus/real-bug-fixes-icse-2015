#!/usr/bin/python
"""
    analyze the list of revisions sent by Hao and creates a bunch of corresponding files


"""
import re
import json
import os

NREQ_PER_DAY=1000

def curl_jira_cmd(bug_id):
    return 'curl -o jira_'+bug_id+'.json https://issues.apache.org/jira/rest/api/latest/issue/'+bug_id

def curl_svn_summary_cmd(revision_number):
    revision_number = int(revision_number)
    prev_revision_number = revision_number -1 
    return 'curl -o '+str(revision_number)+'.xml -X REPORT -H "DAV: http://subversion.tigris.org/xmlns/dav/svn/depth" -H "DAV: http://subversion.tigris.org/xmlns/dav/svn/mergeinfo" -H "DAV: http://subversion.tigris.org/xmlns/dav/svn/log-revprops" -d "<S:update-report xmlns:S=\\"svn:\\"><S:include-props>yes</S:include-props><S:src-path>/repos/asf</S:src-path><S:target-revision>'+str(revision_number)+'</S:target-revision><S:dst-path>http://svn.apache.org/repos/asf</S:dst-path><S:ignore-ancestry>yes</S:ignore-ancestry><S:text-deltas>no</S:text-deltas><S:depth>unknown</S:depth><S:entry rev=\\"'+str(prev_revision_number)+'\\" depth=\\"infinity\\"/></S:update-report>" -v \'https://svn.apache.org/repos/asf/!svn/me\''

def analyze_lucene():
    analyze_file('lucene')

def analyze_file(identifier):
    l = []
    res_str=""
    dl_svn_summary_str=""
    dl_jira_str=""
    jira_uniq = {}
    n_log_already_downloaded = 0
    n_jira = 0
    n_jira_already_downloaded = 0
    n_revisions=0
    for line in open(identifier+'-bug-fix-commits-orig.txt'):
        n_revisions+=1
        res = {}
        mo = re.match(r'.*?([0-9]+)_([A-Z]+-[0-9]+|internal).*$', line)
        
        revision_id = mo.group(1)
        n_log_already_downloaded
        
        if os.path.isfile("svn.d/"+revision_id+'.xml'):
            n_log_already_downloaded+=1
        else:
            pass
        dl_svn_summary_str+=curl_svn_summary_cmd(revision_id)+"\nsleep 1s\n"

        res_str+=revision_id+"\n"
        res['revision_id'] = revision_id
        
        bug_report_id = mo.group(2)
        
        if bug_report_id == "internal":
            res['selection_criterion'] = "commit message contain bug or fix"
        else:
            n_jira+=1
            jira_uniq[bug_report_id]=True
            res['selection_criterion'] = "commit message contains a JIRA identifier"
            #print "jira/jira_"+bug_report_id+'.json'
            if not os.path.isfile("jira/jira_"+bug_report_id+'.json'):
                dl_jira_str += curl_jira_cmd(bug_report_id)+"\nsleep 1s\n"
            else:
                n_jira_already_downloaded += 1
            
        res['bug_report_id'] = bug_report_id
        
        l.append(res)
        
    print len(jira_uniq),n_jira,"bug reports"
    txt_file = identifier+'-bug-fix-commits-ls.txt'
    f = open(txt_file,"w")
    f.write(res_str)
    f.close()
    print "written ",txt_file
    
    
    sh_file = identifier+'-dl-svn.sh'
    f = open(sh_file,"w")
    f.write(dl_svn_summary_str)
    f.close()
    print "written ",sh_file

    sh_jira_file = identifier+'-dl-jira.sh'
    f = open(sh_jira_file,"w")
    f.write(dl_jira_str)
    f.close()
    print "written ",sh_jira_file

    json_file = identifier+'-bug-fix-commits.json'
    with open(json_file, 'w') as outfile:
        json.dump(l, outfile, indent=1, sort_keys=True, encoding="utf-8")
    print "written ",json_file
    
    print str(len(l))+ " commits"
    print "n_log_already_downloaded ",n_log_already_downloaded,'/',n_revisions
    print "n_jira_already_downloaded ",n_jira_already_downloaded,'/',n_jira
    
analyze_file('lucene')
analyze_file('aries')
analyze_file('mahout')
analyze_file('derby')
analyze_file('cassandra')

