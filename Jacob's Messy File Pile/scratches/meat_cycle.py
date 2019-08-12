###okay so this will just be a script for analyzing a membrane skinner cycle
###will be using the "meat_grabber" definition for a cycle, e.g. period of multiple reads where right hand yaw > 20
###Biggest challenges: Should be left and right hand values here.
class MembraneCycle(object):
    _left = None
    _right = None
    _cycles = None
    _yaws = None
    _pitches = None
    _rolls = None
    _time = None

    def __init__(self, expy1, expy2):
        self._left=expy1
        self._right=expy2
        lefty = expy1._yaw
        leftyp = expy1._pitch
        leftyr = expy1._roll
        righty = expy2._yaw
        rightyp = expy2._pitch
        rightyr = expy2._roll
        pitch = {}
        pitch['left'] = leftyp
        pitch['right'] = rightyp
        roll = {}
        roll['left'] = leftyr
        roll['right'] = rightyr
        yaw = {}
        yaw['left'] = lefty
        yaw['right'] = righty
        self._rolls = roll
        self._yaws = yaw
        self._pitches = pitch
        self._time={}
        timy=expy1.time
        timr=expy2.time
        self._time['right'] = timr
        self._time['left'] = timy






class Cycle(object):
    _yaw = None
    _pitch = None
    _roll = None
    _motion = None
    _speed = None
    _posture = None
    _time = None

    def __init__(self, yaw, pitch, roll, time):
        #Okay, yaw/pitch/roll will each be a dictionary with pointers to 'left' and 'right'
        self._yaw = yaw
        self._pitch = pitch
        self._roll = roll
        self._time = time
        #so need to go through the right and look at yaw values

class Entries(object):
    _leftexperiment = None #holds the experiment in question
    _rightexperiment = None
    _entrylist = None #holds a list of entries
    _timelistl = None
    _timelistr = None

    def __init__(self, experl, experr):
        self._leftexperiment = experl
        self._rightexperiment = experr
        self._entrylist = {}
        self._timelistl = list(experl.time)
        self._timelistr = list(experr.time)
        leftSize = len(self._leftexperiment.time)
        rightSize = len(self._rightexperiment.time)
        #using times as keys, hopefully overlap will get us the info we want!
        entry=0
        while entry < rightSize:
            time = self._timelistr[entry]
            nuEntry = Entry(experr, entry, time)
            self._entrylist[time]=[None, nuEntry]
            entry = entry + 1
            #print(entry)
        entry=0
        while entry < leftSize:
            time = self._timelistl[entry]
            nuEntry = Entry(experl, entry, time)
            try:
                self._entrylist[time][0]=nuEntry
            except:
                print ("failed to append values for " + str(time))
            entry = entry + 1
            #print(entry)





efff=Entries(hi1, hi2)

class Entry(object):
    _pitch = None
    _yaw = None
    _roll = None
    _time = None
    _hand = None

    def __init__(self, exper, nval, time):
        self._pitch = {}
        self._pitch['hand']=exper._pitch['hand'][nval]
        self._pitch['wrist']=exper._pitch['wrist'][nval]
        self._pitch['delta']=exper._pitch['delta'][nval]
        self._yaw = {}
        self._yaw['hand'] = exper._yaw['hand'][nval]
        self._yaw['wrist'] = exper._yaw['wrist'][nval]
        self._yaw['delta'] = exper._yaw['delta'][nval]
        self._roll = {}
        self._roll['hand'] = exper._roll['hand'][nval]
        self._roll['wrist'] = exper._roll['wrist'][nval]
        self._roll['delta'] = exper._roll['delta'][nval]
        timez=list(exper._time)
        self._time=time
        self._hand = exper._meta_data['hand']

    def time(self):
        return self._time

    def pitch(self):
        return self._pitch

    def yaw(self):
        return self._yaw

    def roll(self):
        return self._roll



#need to use time




#I think most of the above is a wash
#So... onesec.py and the Seconds class

#So have an experiments object exps
#Want to pull out scores for workers (metrics) from each experiment
#So let's sort this by worker
import os
import matplotlib.pyplot as plt
import numpy as np
os.sys.path.append('C:\\Users\\Jacob\\Documents\\Data_Analytics\\Analytics')
import experiment
import numpy as np
import matplotlib.pyplot as plt

from sklearn.datasets import load_iris
from sklearn.decomposition import PCA, IncrementalPCA

basepath_structured = r"C:\\Users\\Jacob\\Documents\\Trial_Data"
exps = experiment.Experiments(basepath=basepath_structured, is_structured=True,
                 cache_path='cache_QC_Automated.pkl')

meteors={}
for exper in exps._experiments:
    name=exper.name.split('_')
    worker=name[3]
    task=name[2]
    if task not in meteors.keys():
        meteors[task]={}
    if worker not in meteors[task].keys():
        meteors[task][worker]=[]
    meteors[task][worker].append(exper)

trial=Seconds(meteors['MembraneSkinner']['Patricia'][3])

X=[]
for second in trial._seconds:
    X.append(second._features)
pca=PCA(n_components=2)
X_eh= pca.fit(X)
X_r=pca.fit(X).transform(X)

X_eh= pca.fit_transform(X)

maxy = 0
for value in X_eh:
    if max(value) > maxy:
        maxy=max(value)

for value in X_eh:
    value[0]=value[0]/maxy
    value[1]=value[1]/maxy

for value in X_eh:
    plt.scatter(value[0], value[1])



from time import time
import numpy as np
import matplotlib.pyplot as plt

from sklearn import metrics
from sklearn.cluster import KMeans
from sklearn.datasets import load_digits
from sklearn.decomposition import PCA
from sklearn.preprocessing import scale
#KMeans attempt?
data=scale(X)
n_samples, n_features=data.shape
n_digits = len(X)

oK=KMeans(init="k-means++", n_clusters = 10, n_init=10)
fat = oK.fit(data)


reduced_data = PCA(n_components=2).fit_transform(data)
kmeans = KMeans(init='k-means++', n_clusters=4, n_init=10)
kmeans.fit(reduced_data)

# Step size of the mesh. Decrease to increase the quality of the VQ.
h = .02     # point in the mesh [x_min, x_max]x[y_min, y_max].

# Plot the decision boundary. For that, we will assign a color to each
x_min, x_max = reduced_data[:, 0].min() - 1, reduced_data[:, 0].max() + 1
y_min, y_max = reduced_data[:, 1].min() - 1, reduced_data[:, 1].max() + 1
xx, yy = np.meshgrid(np.arange(x_min, x_max, h), np.arange(y_min, y_max, h))

# Obtain labels for each point in mesh. Use last trained model.
Z = kmeans.predict(np.c_[xx.ravel(), yy.ravel()])

# Put the result into a color plot
Z = Z.reshape(xx.shape)
plt.figure(1)
plt.clf()
plt.imshow(Z, interpolation='nearest',
           extent=(xx.min(), xx.max(), yy.min(), yy.max()),
           cmap=plt.cm.Paired,
           aspect='auto', origin='lower')

plt.plot(reduced_data[:, 0], reduced_data[:, 1], 'k.', markersize=2)
# Plot the centroids as a white X
centroids = kmeans.cluster_centers_
plt.scatter(centroids[:, 0], centroids[:, 1],
            marker='x', s=169, linewidths=3,
            color='w', zorder=10)
plt.title('K-means clustering on Membrane Skinner, Patricia, Right Hand Segment 2 (PCA-reduced data)\n'
          'Centroids are marked with white cross')
plt.xlim(x_min, x_max)
plt.ylim(y_min, y_max)
plt.xticks(())
plt.yticks(())
plt.show()


useThis=trial._experiment

def segment(start, count, experiment):
    stop=start+count
    yawz=experiment.yaw(loc='hand')[start:stop]
    pitchz=experiment.pitch(loc='hand')[start:stop]
    return [yawz, pitchz]

def redden(listy):
    n=0
    nuList=[[],[]]
    maxYaw=max(listy[0])
    maxPitch=max(listy[1])
    while n < len(listy[0]):
        nuYaw=(listy[0][n]*10)maxYaw
        nuPitch=(listy[1][n]*6)/maxPitch
        nuList[0].append(nuYaw)
        nuList[1].append(nuPitch)
        n=n+1
    return nuList


seggy=segment(5000, 600, useThis)

nuSeggy=redden(seggy)

plt.plot(nuSeggy[0], nuSeggy[1])



#from sklearn.decomposition import RandomizedPCA
#pca = RandomizedPCA(150)
#pca.fit(faces.data)

pca=PCA(n_components=16)
pca.fit(data)
plt.plot(np.cumsum(pca.explained_variance_ratio_))
plt.xlabel('number of components')
plt.ylabel('cumulative explained variance');
plt.show()