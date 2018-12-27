import pickle
import numpy as np

model = pickle.load(open("som.pkl","rb"))
comments = pickle.load(open("comments_.pkl","rb"))

model.train_batch(comments,len(comments)*250)
pickle.dump(model,open("som_1.pkl","wb"))

