import re
import pickle

word = ['security','CVE','NVD','securities','vulnerability','Cross-Site Scripting','XSS')]

comments = pickle.load("comments_vec.pkl","wb")

vul_list = []
for i,comment in enumerate(comments):
    if w in word:
        vul_list.append(i)
