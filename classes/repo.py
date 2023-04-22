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
        self.closed_issues_count = sum(1 for element in self.issues if element['state'] == 'closed')
        self.prs = self.__query_github(f'repos/{self.org_name}/{self.repo_name}/pulls?state=all')        
        self.open_pr_count = sum(1 for element in self.prs if element['state'] == 'open')
        self.closed_pr_count = sum(1 for element in self.prs if element['state'] == 'closed')

    @staticmethod
    def full_report(org_name, repo_name):
        my_ghrepo = Repo(org_name, repo_name)
        my_ghrepo.md_repo()
        my_ghrepo.md_contributors()
        
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
            
        # Print the number of open and closed issues
        print(f"\n### Issues\n\nOpen: {self.repo['open_issues_count']}<br/>\nClosed: {self.closed_issues_count}")

        # Print the number of open and closed prs
        print(f"\n### Pull requests\n\nOpen: {self.open_pr_count}<br/>\nClosed: {self.closed_pr_count}")
                  
    def md_contributors(self):
        """Qutput in MarkDown the list of contributors to the repository.

        Returns:
            None
        """
        print(f"\n### Contributors")
        for contributor in self.contributors:
            print(
                f"- [{contributor['login']}]({contributor['html_url']}) ({contributor['contributions']})")

