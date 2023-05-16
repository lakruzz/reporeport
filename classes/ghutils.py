import json
import os
import sys
import subprocess

class_path = os.path.dirname(os.path.abspath(__file__))+"/classes"
sys.path.append(class_path)

class Ghutils:
    
  @staticmethod
  def get_element_count(json:str, key:str, value:str,):
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
