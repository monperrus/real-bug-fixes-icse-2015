#!/usr/bin/python
"""
  combines svn and json files

  and creates output_file_name = 'bug-fix-commit-dataset.json'

"""
import xmltodict
import re
import json
import os
import shutil
import sys
from collections import OrderedDict

def list_changed_files(d,prefix,result):
    """ extracts a list of changed files from a low-level XML from SVN """
    if d.has_key('@name'): prefix += '/'+d['@name']
    
    if d.has_key('S:open-directory'):
        #print 'open-dir'
        if type(d['S:open-directory']) == list: 
            for i in d['S:open-directory']:
                list_changed_files(i,prefix,result)
        else:
            list_changed_files(d['S:open-directory'],prefix,result)
            
    # modified
    if d.has_key('S:open-file'):
        #print 'open-file'
        if type(d['S:open-file']) == list: 
            for i in d['S:open-file']:
                result.append({"name":prefix+"/"+i['@name'],"type":"modified"})
        else:
            result.append({"name":prefix+"/"+d['S:open-file']['@name'],"type":"modified"})
            
    # added
    if d.has_key('S:add-file'):
        if type(d['S:add-file']) == list: 
            for i in d['S:add-file']:
                result.append({"name":prefix+"/"+i['@name'],"type":"added"})
        else:
            result.append({"name":prefix+"/"+d['S:add-file']['@name'],"type":"added"})

    # delete
    if d.has_key('S:delete-entry'):
        if type(d['S:delete-entry']) == list: 
            for i in d['S:delete-entry']:
                result.append({"name":prefix+"/"+i['@name'],"type":"deleted"})
        else:
            result.append({"name":prefix+"/"+d['S:delete-entry']['@name'],"type":"deleted"})

    return result

        
    
def create_for(identifier):
    result = []
    for line in open(identifier+'-bug-fix-commits-orig.txt'):
        
        res = OrderedDict()
        mo = re.match(r'.*?([0-9]+)_([A-Z]+-[0-9]+|internal).*$', line)
        revision_id = mo.group(1)
        
        
        res["project"] = identifier
        res['revision_id'] = revision_id
        

        # old version, using JSON files
        # commit_msg, commit_author and commit_date come from data
        #data = json.loads(open('data/'+revision_id+".json").read())
        #res["commit_msg"] = [e.strip() for e in data["msg"].split("\n") if e.strip()!=""  ]        
        #res["commit_author"] = data["author"].strip()
        #res["commit_date"] = data["date"].strip()

        # new version using XML from SVN
        xml_file = "log.d/"+revision_id+'.xml'
        if not os.path.isfile(xml_file): continue

        svn_commit = xmltodict.parse(open(xml_file).read())['S:log-report']['S:log-item']
        res["commit_msg"] = [e.strip() for e in svn_commit["D:comment"].split("\n") if e.strip()!=""  ]
        res["commit_author"] = svn_commit["D:creator-displayname"].strip()
        res["commit_date"] = svn_commit["S:date"].strip()

        xml_file = "svn.d/"+revision_id+'.xml'
        svn_logs = xmltodict.parse(open(xml_file).read())
        #print json.dumps(svn_logs, indent=1, sort_keys=True)    
        res['changed_files'] = list_changed_files(svn_logs["S:update-report"],'',[])
        
        bug_report_id = mo.group(2)
        

        if bug_report_id == "internal":
            res['selection_criterion'] = "commit message contains bug or fix"
            result.append(res)
        else:
            res['selection_criterion'] = "commit message contains a JIRA identifier"

            if not re.match('.*'+bug_report_id.replace('-','.')+'.*', " ".join(res["commit_msg"]), re.IGNORECASE | re.MULTILINE | re.DOTALL ):
                print ('inconsistency found! no Jira bug identifier in '+ bug_report_id+ ' ')
                continue
            else: 
                #print "OK ",bug_report_id
                pass

            try:
                jira_report = json.loads(open("jira.d/jira_"+bug_report_id+'.json').read())
            except ValueError as e:
                # for instance jira.d/jira_CASSANDRA-2351.json is unauthorized and return XML error
                result.append(res)
                continue
            #except IOError as e:
                #result.append(res)
                #continue
            
            # Jira were not downloaded
            if "errorMessages" in jira_report:
                result.append(res)
                continue

            jira_simple_report={}
            jira_simple_report['bug_report_id'] = bug_report_id
            jira_simple_report['issuetype'] = jira_report['fields']['issuetype']['name']
            jira_simple_report['priority'] = jira_report['fields']['priority']['name']
            
            # resolution
            # sometimes is null
            resolution = 'unknown'
            if jira_report['fields']['resolution']:
                resolution = jira_report['fields']['resolution']['name']
            res['jira_bug_report'] = jira_simple_report
            jira_simple_report['resolution'] = resolution
            if not jira_report['fields']['description']: jira_report['fields']['description'] = ""
            
            jira_simple_report['description'] = [e.strip() for e in jira_report['fields']['description'].split("\n") if e.strip()!=""  ]

            if res['jira_bug_report']['issuetype']=='Bug':
                result.append(res)
                #print res['jira_bug_report']
    return result

l=[]

output_file_name = 'target/bug-fix-commit-dataset.json'


l = l+ create_for('mahout')
l = l+ create_for('derby')
l = l+ create_for('cassandra')
l = l+ create_for('lucene')
l = l+ create_for('aries')

with open(output_file_name, 'w') as outfile: json.dump(l, outfile, indent=1)    
print "written ",output_file_name

import hashlib
if hashlib.sha1(open(output_file_name).read()).hexdigest() != hashlib.sha1(open(os.path.basename(output_file_name)).read()).hexdigest():
    raise Exception('not the right file')
