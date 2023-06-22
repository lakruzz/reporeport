Assuming you have `gh`installed and it's setup correctly - to test it run

```shell
 gh auth status
````


Never make a change without an issue:

```shell
gh issue create -t "title" -b "Body" -a @me
```

Capture the issue number (e.g. 13)

Create a branch for the specific issue before you add commit anything:

```shell
gh issue develop -c 13
````

Create a pull request on your issue branch.

_...While checked out on the issue branch_

```shell
gh pr create
```

Capture the pr number (e.g 16)

To merge it in:

```shell
gh pr merge 16 --squash --auto --delete-branch
``` 


While you work on the issus - add the necessary tests for what ever you are changing, keep them there when you are done. I you thing they have relevant for hte Continuous Integration test.

Mark them with 

```python
@pytest.mark.smoke
def test_ghutils_query_github_incl_headers(api, die_on_error=False):
```
remember test functions must start with `test_``

