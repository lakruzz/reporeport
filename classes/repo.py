import subprocess
import json
import sys
import base64
import os

# Add directory of this class to the general class_path
# to allow import of sibling classes
class_path = os.path.dirname(os.path.abspath(__file__))
sys.path.append(class_path)

from ghutils import Ghutils

class Repo:
    """
    A class to represent a GitHub repository.
    """    
    def __init__(self, org_name, repo_name):
        self.org_name = org_name
        self.repo_name = repo_name
        
        _,self.repo = Ghutils.query_github(f'repos/{self.org_name}/{self.repo_name}')
        _,self.contributors = Ghutils.query_github(f'repos/{self.org_name}/{self.repo_name}/contributors')
        _,self.issues = Ghutils.query_github(f"repos/{self.org_name}/{self.repo_name}/issues?state=all")
        _,self.prs = Ghutils.query_github(f'repos/{self.org_name}/{self.repo_name}/pulls?state=all')
        _,self.commits = Ghutils.query_github(f'repos/{self.org_name}/{self.repo_name}/commits')
        
        self.open_issues_count = self.repo['open_issues_count']
        self.closed_prs_count = Ghutils.get_element_count(self.prs, 'state', 'closed')
        self.open_prs_count = Ghutils.get_element_count(self.prs, 'state', 'open')
        self.closed_issues_count = Ghutils.get_element_count(self.issues, 'state', 'closed')
        
    def get_issue_by_title(self,regex):
        json_obj = Ghutils.get_element_by_regex(self.issues,'title',regex)
        if json_obj is not None:
            return json_obj['number']
        elif json_obj is None:
            return None

    @staticmethod
    def full_report(org_name, repo_name):
        my_ghrepo = Repo(org_name, repo_name)
        my_ghrepo.md_repo()
        my_ghrepo.md_contributors()
        my_ghrepo.md_get_codeowners()   
        # print (my_ghrepo.get_issue_by_title('.*CSS.*'))
        Ghutils.buffer_to_stdout()    
        
    def md_get_codeowners(self):
        # Retrieve the CODEOWNERS file content and decode it from base64
           status,codeowners_file = Ghutils.query_github(f'repos/{self.org_name}/{self.repo_name}/contents/CODEOWNERS',False)  
           if status != 0:
               Ghutils.print_to_buffer(f"- [ ] CODEOWNERS file")
           else:
               codeowners = base64.b64decode(codeowners_file['content']).decode('utf-8')
               # Regular expression pattern to match mentions of @user or @team
               owner_pattern = r"@([\w\-\/]+)"
               # Loop through each line in the codeowners file, extract the owners and print them
               owners = []
               for line in codeowners.split("\n"):
                   # Skip comments and blank lines
                   if line.lstrip().startswith("#") or not line.strip():
                       continue
                   
                   # Use the regular expression to find all owners in the line
                   line_owners = re.findall(owner_pattern, line)
                   # Remove duplicates and print the owners found in the line
                   if line_owners:
                       owners.extend(line_owners)
               
               for owner in list(set(owners)):
                   Ghutils.print_to_buffer(f"  - @{owner}")
 
    def md_repo(self):
        """Output in MarkDown the details of the repository.

        Returns:
            None
        """

        # Print the full name of the repo in a header and link to both org and repo
        Ghutils.print_to_buffer(
            f"## [{self.repo['owner']['login']}]({self.repo['owner']['html_url']})/[{self.repo['name']}]({self.repo['html_url']})")
        
        # Print the description of the repo if it exists
        if self.repo['description'] is not None:
            Ghutils.print_to_buffer( f"\n_{self.repo['description']}_")
        
        # Print a mermaid pie with numbers of open and closed issues and PRs
        template = '''
### Issues and PRs\n
```mermaid
pie showData title Issues and PRs
"Issues: open" : {}
"Issues: closed" : {}
"PRs : open" : {}
"PRs :closed" : {}
```'''
        Ghutils.print_to_buffer(
            template.format(self.open_issues_count, self.closed_issues_count, self.open_prs_count, self.closed_prs_count))
                  
    def md_contributors(self):
        """
        Qutput in MarkDown the list of contributors to the repository.

        Returns:
            None
        """
        Ghutils.print_to_buffer(f"\n### Contributors\n")
        mermaid = '''
```mermaid
pie showData title Contributors (number of commits)
'''
        for contributor in self.contributors:
            _,user = Ghutils.query_github(f"users/{contributor['login']}")
            bullet = '- [ ]'
            name = f'_Name is not set - [fix it!]({Ghutils.change_ghname_url})_ '
            if user['name'] is not None:
                bullet = f'- [x]'
                name = f"_{user['name']}_"
            Ghutils.print_to_buffer(
                f"{bullet} [{contributor['login']}]({contributor['html_url']}) {name} ([{contributor['contributions']}](https://github.com/{self.org_name}/{self.repo_name}/commits?author={contributor['login']}))")
            mermaid += f'"{contributor["login"]}" : {contributor["contributions"]}\n'
        Ghutils.print_to_buffer(       mermaid + "\n```\n")
    

