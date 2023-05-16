import subprocess
import json
import sys
import base64
import os

class_path = os.path.dirname(os.path.abspath(__file__))
sys.path.append(class_path)

from ghutils import Ghutils

class Repo:
    change_ghname_url = "https://docs.github.com/en/account-and-profile/setting-up-and-managing-your-personal-account-on-github/managing-personal-account-settings/changing-your-github-username#changing-your-username"
    
    def __init__(self, org_name, repo_name):
        self.org_name = org_name
        self.repo_name = repo_name
        _,self.repo = Ghutils.query_github(f'repos/{self.org_name}/{self.repo_name}')
        _,self.contributors = Ghutils.query_github(f'repos/{self.org_name}/{self.repo_name}/contributors')
        _,self.issues = Ghutils.query_github(f"repos/{self.org_name}/{self.repo_name}/issues?state=all")
        self.closed_issues_count = Ghutils.get_element_count(self.issues, 'state', 'closed')
        self.open_issues_count = self.repo['open_issues_count']
        _,self.prs = Ghutils.query_github(f'repos/{self.org_name}/{self.repo_name}/pulls?state=all')
        self.closed_prs_count = Ghutils.get_element_count(self.prs, 'state', 'closed')
        self.open_prs_count = Ghutils.get_element_count(self.prs, 'state', 'open')
        _,self.commits = Ghutils.query_github(f'repos/{self.org_name}/{self.repo_name}/commits')
        
        
    def __get_codeowners(self,markdown=True):
        # Retrieve the CODEOWNERS file content and decode it from base64
           status,codeowners_file = self.__query_github(f'repos/{self.org_name}/{self.repo_name}/contents/CODEOWNERS',False)  
           if status != 0:
               if markdown == True:
                   print (f"- [ ] CODEOWNERS file")
               else:
                   print (f"CODEOWNERS file not found") 
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
               return list(set(owners))
   
    @staticmethod
    def full_report(org_name, repo_name):
        my_ghrepo = Repo(org_name, repo_name)
        my_ghrepo.md_repo()
        my_ghrepo.md_contributors()
        my_ghrepo.__get_codeowners(True)
        
    def __query_github(self, ghapi:str, die_on_error:bool=True):
        """
        Query GitHub's API. 
        More details at https://docs.github.com/en/rest

        Args:
            api (str): The exact API to query GitHub

        Returns:
            json: The reply from the query
        """
        try:
            # Call the GitHub API
            response = subprocess.run(
                ['gh', 'api', ghapi], capture_output=True, text=True, check=True)
            
            # Parse the JSON output of the API call
            return response.returncode,json.loads(response.stdout)

        except subprocess.CalledProcessError as e:
            if die_on_error:
                print(f"Error: {e.stderr}", file=sys.stderr)
                sys.exit(1)
            else:
                return e.returncode, f"Error: {e.stderr}"

    def md_repo(self):
        """Output in MarkDown the details of the repository.

        Returns:
            None
        """

        # Print the full name of the repo in a header and link to both org and repo
        print(
            f"## [{self.repo['owner']['login']}]({self.repo['owner']['html_url']})/[{self.repo['name']}]({self.repo['html_url']})")
        
        # Print the description of the repo if it exists
        if self.repo['description'] is not None:
            print( f"\n_{self.repo['description']}_")
        
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
        print (template.format(self.open_issues_count, self.closed_issues_count, self.open_prs_count, self.closed_prs_count))
                  
    def md_contributors(self):
        """Qutput in MarkDown the list of contributors to the repository.

        Returns:
            None
        """
        print(f"\n### Contributors\n")
        mermaid = '''
```mermaid
pie showData title Contributors (number of commits)
'''
        for contributor in self.contributors:
            _,user = self.__query_github(f"users/{contributor['login']}")
            bullet = '- [ ]'
            name = '_Name is not set - [fix it!]({change_ghname_url})_ '
            if user['name'] is not None:
                bullet = f'- [x]'
                name = f"_{user['name']}_"    
            print(
                f"{bullet} [{contributor['login']}]({contributor['html_url']}) {name} ([{contributor['contributions']}](https://github.com/{self.org_name}/{self.repo_name}/commits?author={contributor['login']}))")
            mermaid += f'"{contributor["login"]}" : {contributor["contributions"]}\n'
        print (mermaid + "\n```\n")
    

