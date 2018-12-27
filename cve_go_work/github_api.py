import requests
import re
import pickle
import time
import random
api_link = "https://api.github.com/repos"
repo_path = "/kubernetes/kubernetes"
# repo_path = "/dgonyeo/acpush"
# repo_path = "/noironetworks/aci-containers"
# repo_path = "/Azure/acs-engine"
# repo_path = "/GoogleCloudPlatform/agones"
# issues_link = "/issues"
issues_link = "/issues?state=all"
pull_link = "/pulls?state=all"
# pull_link = "/pulls"
Stop_Flag = False

token_list = pickle.load(open("token.pkl","rb"))
token_idx = random.randint(0,len(token_list)-2)

# def request_github_api(url):
#     global token_idx
#     global Stop_Flag
#     r = requests.get(url,headers={'Authorization': 'token ' + token_list[token_idx] })
#     if int(r.headers['X-RateLimit-Remaining']) > 5 and "200" in r.headers['Status']:
#         return r
#     else:
#         if token_idx != len(token_list) - 1 and "200" in r.headers['Status']:
#             token_idx += 1
#             return r
#         elif "200" in r.headers['Status']:
#             print(r.headers)
#             Stop_Flag = False
#             return r
#         else:
#             token_idx = 0
#             return r

def request_github_api(url):
    global token_idx
    global Stop_Flag
    r = requests.get(url,headers={'Authorization': 'token ' + token_list[token_idx] })
    if int(r.headers['X-RateLimit-Remaining']) > 300 and "200" in r.headers['Status']:
        return r
    else:
#         if token_idx != len(token_list) - 1 and "200" in r.headers['Status']:
        if "200" in r.headers['Status']:
            token_idx = (token_idx + 1) % len(token_list)
            return r
        else:
            print(r.headers)
            Stop_Flag = True
            return r

def next_page_link(req):
    if "Link" in dict(req.headers).keys():
        links = re.sub("<|>|;|,"," ",req.headers["link"]).split()
        try:
            return True,links[links.index("rel=\"next\"") - 1]
        except:
            return False,False        
    else:
        print("No Links")
        return False,False


def extract_github_issue(req_issue_list,issue_dict):
    for issue_sn in range(len(req_issue_list)):
        issue = ''
        issue_json = req_issue_list[issue_sn]
        if issue_json.get("title") != None:
            issue += issue_json['title'] + ".\n "
        if issue_json.get("body") != None:
            issue += issue_json['body'] + ".\n "
        # extract all the link from issue comment
        print("extract_github_issue: " + issue_json['comments_url'])
        req_issue_comment = request_github_api(issue_json['comments_url'])
        issue_comment_json = req_issue_comment.json()
        for i in range(len(issue_comment_json)):
            if Stop_Flag == True:
                pickle.dump(issue_dict,open("test.pk","wb"))
                return False
            if issue_comment_json[i].get("body") != None:
                issue += issue_comment_json[i]['body'] + ".\n "
        issue_dict[issue_json['number']] = issue
    return True

def extract_all_issue(url):
    global Stop_Flag
    req_issue_list = request_github_api(url)
    # print("req_issue_list %s" % (req_issue_list.json()))
    if Stop_Flag == True:
        Stop_Flag = False
        return {}
    issue_dict = {}
    try:    
        extract_github_issue(req_issue_list.json(),issue_dict)
        is_next, page_link = next_page_link(req_issue_list)
        while is_next and not Stop_Flag:
            print("extract_all_issue " + page_link)
            req_issue_next_page = request_github_api(page_link)
            if Stop_Flag == True:
                Stop_Flag = False
                return issue_dict
            extract_github_issue(req_issue_next_page.json(),issue_dict)
            is_next, page_link = next_page_link(req_issue_next_page)
            if len(issue) == 0:
                continue
            else:
                pickle.dump(issue,open("./repo/" + repo_path.replace("/","") + "_pull","wb"))
    except Exception as e:
        print('Error occurred : ' + str(e))
        if len(issue) == 0:
            pass
        else:
            pickle.dump(issue,open("./repo/" + repo_path.replace("/","") + "_pull","wb"))
    return issue_dict

repo_list = pickle.load(open("repos_list.pkl","rb"))

def extract(a,b):
    for repo in repo_list[a:b]:
        repo_path = repo.replace("https://github.com","")
        # print(api_link + repo_path + issues_link)
        print(api_link + repo_path + pull_link)
        # issue = extract_all_issue(api_link + repo_path + issues_link)
        extract_all_issue(api_link + repo_path + pull_link)

if __name__ == "__main__":
    issue = extract_all_issue(api_link + repo_path + pull_link)
    pickle.dump(issue,open("./repo/" + repo_path.replace("/","_") + "_pull","wb"))
