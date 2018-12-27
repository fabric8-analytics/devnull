
# coding: utf-8

# In[2]:


import pickle
import numpy as np

# In[6]:


fasttext_dict = pickle.load(open("fasttext_vec.pkl","rb"))
stop_words = pickle.load(open("stopwrd","rb"))
comments = pickle.load(open("processed_comments.pkl","rb"))

def tokenize_comments(comments):
    comments = comments.split()
    comments = [t for t in comments 
                if t not in stop_words and t != '']
    return comments

tokenized_comments = [tokenize_comments(comment)
                         for comment in comments]

def comments_to_vec(tokens):
    words = [word for word in np.unique(tokens) 
            if word in fasttext_dict]
    if len(words) > 0:
        return np.array([fasttext_dict[word] for word in words ])
    else :
        return words = '.'
    
vectorized_comments = [comments_to_vec(comments).mean(axis=0)
                       for comments in tokenized_comments]
vectorized_comments = np.array(vectorized_comments) 
# pickle.dump(vectorized_comments,open("/home/hadoop/comments_vec.pkl","wb"))

print(vectorized_comments.shape)
