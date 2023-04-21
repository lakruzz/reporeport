import subprocess
import json

class Repo:
    def __init__(self, org, repo):
        self.org = org
        self.repo = repo
        self.collaborators = self.__get_collaborators()

    @staticmethod
    def full_report(org, repo):
        my_ghrepo = Repo(org, repo)
        my_ghrepo.md_title()
        my_ghrepo.md_collaborators()
          
    # Call the GitHub API to get the list of collaborators for the specified repository
    def __get_collaborators(self):
        """Get the list of collaborators for a repository.

        Args:
            org (str): The GitHub organization or user
            repo (str): The name of the repository

        Returns:
            list: A list of dictionaries containing the login and html_url fields for each collaborator
        """

        try:
            # Call the GitHub API to get the list of collaborators for the specified repository
            response = subprocess.run(
                ['gh', 'api', f'repos/{self.org}/{self.repo}/contributors'], capture_output=True, text=True, check=True)

            # Parse the JSON output of the API call
            collaborators = json.loads(response.stdout)

            # Extract the html_url and login fields for each collaborator
            collaborator_info = [{'html_url': collaborator['html_url'],
                                  'login': collaborator['login']} for collaborator in collaborators]

        except subprocess.CalledProcessError as e:
            print(f"Error: {e.stderr}", file=sys.stderr)
            sys.exit(1)
        except Exception as e:
            print(f"Error: {e}", file=sys.stderr)
            sys.exit(1)

        return collaborator_info

    def md_title(self):
        """Output in MarkDown the title for the repository.

        Returns:
            None
        """

        # Print the results
        print(
            f"\n[{self.org}/{self.repo}](https://github.com/{self.org}/{self.repo})")

    def md_collaborators(self):
        """Qutput in MarkDown the list of collaborators for the repository.

        Returns:
            None
        """
        for collaborator in self.collaborators:
            print(
                f"- [{collaborator['login']}]({collaborator['html_url']})")

