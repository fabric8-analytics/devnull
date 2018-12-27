import spacy
import re
import pandas as pd
import numpy as np
import pickle
import nltk
from nltk.corpus import stopwords 
from nltk.tokenize import word_tokenize, sent_tokenize 
stop_words = set(stopwords.words('english'))
def refine_text(x):
    return [re.sub('[^A-Za-z@.]+', ' ', i.strip()).lower() for i in x]
# def remove_stop_word(doc):
#     temp = []
#     for issue in doc:
#         for word in issue:
#             if not word in stop_words:
#                 temp.append()

# nlp = spacy.load("en")
# neg_data = pickle.load( open( "neg_data.p", "rb" ) )
# pos_data = pickle.load( open( "pos_data.p", "rb" ) )

# word_tokens = word_tokenize(example_sent) 

# ref_pos_data = refine_text(pos_data)
# ref_neg_data = refine_text(neg_data)

# filtered_sentence = [w for w in word_tokens if not w in stop_words]

# neg_data  = [[i, 1] for i in neg_data]
# pos_data = [[i, 0] for i in pos_data]

a = "hi wanodwa djwadwa dnwandwa dfalndwandwa, lkndwaldnwa"
print(word_tokenize(a))