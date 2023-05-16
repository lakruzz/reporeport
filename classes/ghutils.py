import json
import os
import re
import sys
import subprocess
from io import StringIO

# Add directory of this class to the general class_path
# to allow import of sibling classes
class_path = os.path.dirname(os.path.abspath(__file__))
sys.path.append(class_path)

class Ghutils:
  change_ghname_url = "https://docs.github.com/en/account-and-profile/setting-up-and-managing-your-personal-account-on-github/managing-personal-account-settings/changing-your-github-username#changing-your-username"
  __buffer = StringIO()
  
  @staticmethod
  def print_to_buffer(content):
      print(content, file=Ghutils.__buffer)
      
  @staticmethod
  def buffer_to_stdout():
      print(Ghutils.__buffer.getvalue())
      
  @staticmethod
  def buffer_to_file(location: str = "reporeport.md"):
      with open(location, "w") as f:
          f.write(Ghutils.__buffer.getvalue())

  @staticmethod
  def get_org_repo_from_current_directory():
    result = subprocess.run(['gh', 'repo', 'view', '--json', 'owner,name', '--jq', '.owner.login+"/"+.name'], capture_output=True, text=True)
    if result.returncode == 0:
        return result.stdout.strip()
    else:
        return None
  
  @staticmethod
  def get_element_count(json:json, key:str, value:str,):
    """
    Counts of elements in a json, where key=value
    Args:
        json (str): _description_
        key (str): _description_
        value (str): _description_
    Returns:
        int: count of elements in json where key=value
    """
    return sum(1 for element in json if element[key] == value)   

  @staticmethod
  def query_github(ghapi:str, die_on_error:bool=True):
      """
      Query GitHub's API. 
      More details at https://docs.github.com/en/rest
      Args:
          api (str): The exact API to query GitHub
          die_on_error: If True, exit the program on error. Default: True
      Returns:
          on success:
          int,[]json: The returncode from the query and the json output          
          
          on error:
          int,str: The returncode from the query and the error message
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

  @staticmethod
  def get_element_by_regex(json:json,key:str,search:str):
    """
    Get first element from json where key matches regex
    Args:
        json (json): The json to search
        key (str): The key to the value to search
        regex (str): The regex to match
    Returns:
        On match:
            json: element from json where key matches regex

        On no match:
            None    
    """
    regex = re.compile(search)
    for element in json:
        if key in element and regex.search(element[key]):
            return element
    return None
