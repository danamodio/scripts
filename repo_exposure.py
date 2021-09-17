# https://pygithub.readthedocs.io/en/latest/reference.html
from github import Github
g = Github("<>")

repos = []
for repo in g.get_organization('<>').get_repos():
    print( repo.full_name )
    repos.append( repo.name )
    for fork in repo.get_forks():
        print("[!] Found fork: ", fork.full_name)

for member in g.get_organization('<>').get_members():
    print( member.login, ":", member.name)
    for member_repo in member.get_repos():
        if member_repo.name in repos:
            print("[!]", member_repo.full_name)
