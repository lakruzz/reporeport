import subprocess
import json
import sys

class Repo:
    def __init__(self, org_name, repo_name):
        self.org_name = org_name
        self.repo_name = repo_name
        self.repo = self.__query_github(f'repos/{self.org_name}/{self.repo_name}')
        self.contributors = self.__query_github(f'repos/{self.org_name}/{self.repo_name}/contributors')
        self.issues = self.__query_github(f"repos/{self.org_name}/{self.repo_name}/issues?state=all")
        self.closed_issues_count = self.__get_element_count(self.issues, 'state', 'closed')
        self.open_issues_count = self.repo['open_issues_count']
        self.prs = self.__query_github(f'repos/{self.org_name}/{self.repo_name}/pulls?state=all')
        self.closed_prs_count = self.__get_element_count(self.prs, 'state', 'closed')
        self.open_prs_count = self.__get_element_count(self.prs, 'state', 'open')
        self.commits = self.__query_github(f'repos/{self.org_name}/{self.repo_name}/commits')
    
    def __get_element_count(self, json, key, value,):
        return sum(1 for element in json if element[key] == value)
    
    @staticmethod
    def full_report(org_name, repo_name):
        my_ghrepo = Repo(org_name, repo_name)
        my_ghrepo.md_repo()
        my_ghrepo.md_contributors()
        my_ghrepo.md_commits()
        
    def __query_github(self, ghapi):
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
            return json.loads(response.stdout)

        except subprocess.CalledProcessError as e:
            print(f"Error: {e.stderr}", file=sys.stderr)
            sys.exit(1)

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
            print(
                f"- [{contributor['login']}]({contributor['html_url']}) ({contributor['contributions']})")
            mermaid += f'"{contributor["login"]}" : {contributor["contributions"]}\n'
        print (mermaid + "\n```\n")
    
    def md_commits(self):
        """Output in MarkDown the list of commits to the repository.

        Returns:
            None
        """
        print(f"\n<deatils><summary><h3>Commits</h3></summary>\n")
        for commit in self.commits:
            print(
                f"- [{commit['commit']['message']}]({commit['html_url']})")
            print(f"  by [{commit['author']['login']}]({commit['author']['html_url']})")
            print(f"  on {commit['commit']['author']['date']}\n")
            print("</details>\n")

