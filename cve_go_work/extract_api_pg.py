import requests
import re
import pickle
import time
import random
api_link = "https://api.github.com/repos"
repo_path = "/kubernetes/kubernetes"
issues_link = "/issues?state=all"
pull_link = "/pulls?state=all"
# pull_link = "/pulls"
Stop_Flag = False

token_list = pickle.load(open("token.pkl","rb"))
# token_idx = random.randint(0,len(token_list)-2)
token_idx = 0
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
    # print(req_issue_list)
    # for issue_sn in range(len(req_issue_list)):
    issue_sn = 0
    issue = ''
    issue_json = req_issue_list
    # print(issue_json)
    if issue_json.get("title") != None:
        issue += issue_json['title'] + ".\n "
    if issue_json.get("body") != None:
        issue += issue_json['body'] + ".\n "
    # extract all the link from issue comment
    req_issue_comment = request_github_api(issue_json['comments_url'])
    issue_comment_json = req_issue_comment.json()
    for i in range(len(issue_comment_json)):
        if Stop_Flag == True:
            pickle.dump(issue_dict,open("test.pk","wb"))
            return False
        if issue_comment_json[i].get("body") != None:
            issue += issue_comment_json[i]['body'] + ".\n "
    issue_dict[issue_json['number']] = issue
    
    return issue_dict

def extract_all_issue(links):

    issue_dict = {}
    for link in links:
        repo_path = link.replace("https://github.com","")
    
        global Stop_Flag
        req_issue_list = request_github_api(api_link + repo_path)
    # print("req_issue_list %s" % (req_issue_list.json()))
    # if Stop_Flag == True:
    #     Stop_Flag = False
    #     return {}
    # try:
        extract_github_issue(req_issue_list.json(),issue_dict)
        # is_next, page_link = next_page_link(req_issue_list)
        # while is_next and not Stop_Flag:
        #     print("extract_all_issue " + page_link)
        #     req_issue_next_page = request_github_api(page_link)
        #     if Stop_Flag == True:
        #         Stop_Flag = False
        #         return issue_dict
        #     extract_github_issue(req_issue_next_page.json(),issue_dict)
        #     is_next, page_link = next_page_link(req_issue_next_page)
        #     if len(issue) == 0:
        #         continue
        #     else:
        #         pickle.dump(issue,open("./repo/" + repo_path.replace("/","") + "_pull","wb"))
    # except Exception as e:
    #     print('Error occurred : ' + str(e))
    #     if len(issue_dict) == 0:
    #         pass
    #     else:
    #         # pickle.dump(issue,open("./repo/" + repo_path.replace("/","") + "_pull","wb"))
    #         return issue_dict
    return issue_dict

# repo_list = pickle.load(open("repos_list.pkl","rb"))

links = [
    "https://github.com/kubernetes/kubernetes/issues/71671",
    "https://github.com/kubernetes/kubernetes/issues/71411",
    "https://github.com/kubernetes/kubernetes/issues/70160",
    "https://github.com/kubernetes/kubernetes/issues/68858",
    "https://github.com/kubernetes/kubernetes/issues/66460",
    "https://github.com/kubernetes/kubernetes/issues/65950",
    "https://github.com/kubernetes/kubernetes/issues/62454",
    "https://github.com/kubernetes/kubernetes/issues/62099",
    "https://github.com/kubernetes/kubernetes/issues/60814",
    "https://github.com/kubernetes/kubernetes/issues/60813",
    "https://github.com/kubernetes/kubernetes/issues/60661",
    "https://github.com/kubernetes/kubernetes/issues/60146",
    "https://github.com/kubernetes/kubernetes/issues/54505",
    "https://github.com/kubernetes/kubernetes/issues/53311",
    "https://github.com/kubernetes/kubernetes/issues/48677",
    "https://github.com/kubernetes/kubernetes/issues/48396",
    "https://github.com/kubernetes/kubernetes/issues/45386",
    "https://github.com/kubernetes/kubernetes/issues/43459",
    "https://github.com/kubernetes/kubernetes/issues/42950",
    "https://github.com/kubernetes/kubernetes/issues/40955",
    "https://github.com/kubernetes/kubernetes/issues/40403",
    "https://github.com/kubernetes/kubernetes/issues/40061",
    "https://github.com/kubernetes/kubernetes/issues/35462",
    "https://github.com/kubernetes/kubernetes/issues/34822",
    "https://github.com/kubernetes/kubernetes/issues/34517",
    "https://github.com/kubernetes/kubernetes/issues/23860",
    "https://github.com/kubernetes/kubernetes/issues/22888",
    "https://github.com/kubernetes/kubernetes/issues/21215",
    "https://github.com/kubernetes/kubernetes/issues/20820",
    "https://github.com/kubernetes/kubernetes/issues/20617",
    "https://github.com/kubernetes/kubernetes/issues/20151",
    "https://github.com/kubernetes/kubernetes/issues/16971",
    "https://github.com/kubernetes/kubernetes/issues/13598",
    "https://github.com/kubernetes/kubernetes/issues/13459",
    "https://github.com/kubernetes/kubernetes/issues/13319",
    "https://github.com/kubernetes/kubernetes/issues/11816",
    "https://github.com/kubernetes/kubernetes/issues/10834",
    "https://github.com/kubernetes/kubernetes/issues/9675",
    "https://github.com/kubernetes/kubernetes/issues/2630",
    "https://github.com/kubernetes/kubernetes/issues/1004",
    "https://github.com/kubernetes/kubernetes/issues/598"
    ]


def extract(links):

    # print(api_link + repo_path)
    extract_all_issue(link)


if __name__ == "__main__":
    pickle.dump(extract_all_issue(links),open("test.pkl","wb")) 
    # pickle.dump(issue,open("./repo/" + repo_path.replace("/","_") + "_pull","wb"))
