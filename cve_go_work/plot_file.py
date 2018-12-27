import matplotlib.pyplot as plt
# %matplotlib inline
import pickle
import numpy as np

model1 = pickle.load(open("som.pkl","rb"))
comments1 = pickle.load(open("comments_.pkl","rb"))

map_dim = 20
x = []
y = []
plt.figure(figsize=(16,16))
for i, vec in enumerate(comments1):
    winnin_position = model1.winner(vec)
    # plt.plot(winnin_position[0]+np.random.rand()*.5, 
    #          winnin_position[1]+np.random.rand()*.5)
    x.append(winnin_position[0])
    y.append(winnin_position[1]+np.random.rand()*.5)
    # x.append(winnin_position[0])
    # y.append(winnin_position[1])

plt.xticks(range(map_dim))
plt.yticks(range(map_dim))
plt.grid()
plt.xlim([0, map_dim])
plt.ylim([0, map_dim])
# plt.plot(x,y,'o')
plt.scatter(x,y)
plt.show()