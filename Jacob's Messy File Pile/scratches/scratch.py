import os
import xlrd
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import scipy
import peakutils
from numpy import array
import pickle
import json
import csv
import plotly.graph_objs as go
from plotly.offline import plot

from sklearn.decomposition import PCA, KernelPCA

from scipy.signal import find_peaks
from Analytics import Experiments

#basepath_structured = r"C:\\Users\\Jacob\\Documents\\Trial_Data"
#exps = Experiments(basepath=basepath_structured, is_structured=True,
  #                 cache_path='cache_experiments.pkl')

#arr = exps._experiments[0]




#arr.quadCorrect(180)
#arr.topAndBottom()
from bokeh.plotting import figure, output_file, output_notebook, show

#output_file('default.html')


from random import randint
import numpy as np
from scipy.spatial import ConvexHull


def groupMaker(someValues, numsDevs):
  yaws=np.absolute(someValues[0])
  pitchs=someValues[1]
  rolls=someValues[2]
  yawDev=numsDevs*np.std(yaws)
  pitchDev=numsDevs*np.std(pitchs)
  safeYawmin=np.mean(yaws)-yawDev
  #print(safeYawmin)
  safeYawmax=np.mean(yaws)+yawDev
  #print(safeYawmax)
  safePitchmax=np.mean(pitchs)+pitchDev
  #print(safePitchmax)
  safePitchmin=np.mean(pitchs)-pitchDev
  rollDev=numsDevs*np.std(rolls)
  rollMax=np.mean(rolls)+rollDev
  rollMin=np.mean(rolls)-rollDev
  #print(safePitchmin)
  lowRisk=[]
  higherRisk=[]
  n=0
  while n<len(someValues[0]):
   if (safeYawmin<=yaws[n]<=safeYawmax and safePitchmin<=pitchs[n]<=safePitchmax and rollMin<rolls[n]<rollMax):
     lowRisk.append([yaws[n],pitchs[n],rolls[n]])
   else:
     higherRisk.append([yaws[n],pitchs[n],rolls[n]])
   n=n+1
  return([lowRisk, higherRisk])



def chunkify(exper):
 #chunkySet =[]
 goodSets =[]
 badSets =[]
 n = 0
 lenny = len(exper.get_data())
 chunks = int(lenny / 9000)
 while n < chunks:
     nines = n * 9000
     samples = []
     # print(nines)
     for something in np.arange(0, 4, 1):
         samples.append(randint(nines, nines + 9000))
     for samp in samples:
         thisYaSample = exper.yaw(delta=True)[samp:(samp + 1200)]
         thisPiSample = exper.pitch(delta=True)[samp:(samp + 1200)]
         thisRollSample = exper.roll(delta=True)[samp:(samp+1200)]
         if (np.std(thisYaSample)>10 and np.std(thisPiSample)>10 and np.std(thisRollSample > 10)):
          groupz=groupMaker([np.array(thisYaSample),np.array(thisPiSample), np.array(thisRollSample)], 2)
          goodSets.append(groupz[0])
          badSets.append(groupz[1])
     n = n + 1
 return([goodSets, badSets])



def deMirror(sampleset):
    exes=[]
    for pnt in sampleset:
        exes.append(pnt[0])
    center=np.mean(exes)
    #print(center)
    newSet=[]
    for pnt in sampleset:
        #print(pnt)
        if pnt[0]>center:
            exxDif=center-pnt[0]
            #distance from the middle point
            newExx=center-np.absolute(exxDif)
            newPnt=[newExx,pnt[1],pnt[2]]
            #print(newExx)
            newSet.append(newPnt)
            #print(newPnt)
        else:
            newSet.append(pnt)
            #print(pnt)
    return(newSet)




def scatterSample(sampleset):
    exx=[]
    yyy=[]
    rrrr=[]
    #print('ScatterSample')
    #print(sampleset)
    for pnt in sampleset:
     #   print(pnt)
        try:
         exx.append(pnt[0])
         yyy.append(pnt[1])
         rrrr.append(pnt[2])
        except:
            print("That weird error in lengths popped up")
    return([exx,yyy,rrrr])



#data=chunkify(arr)

def areaChunk(chunks):
 """
 Takes an experiment processed into goodSets and badSets via the chunkify function
 Calcualtes the area for each of the subsamples in goodSets and returns them in a list.
 :param chunks:
 :return:
 """
 newSizes=[]
 check=chunks[0]
 n=0
 while n < len(check):
     check[n]=deMirror(check[n])
     n=n+1
 for set in check:
   newSizes.append(ConvexHull(set).area)
 return(newSizes)


#Create a plot that has on the
#X axis: bins of angle movements (in both negative and positive direction (0-15; 15-30; 30-45; 45+)
#Y axis: frequency or total of movements in that angle range
#This one plot will be used to demonstrate the analysis
#Then create a function that summarizes this distribution (integral of the bell curve?). We will show that this value is how we summarize this

def binning(sample, degs):
    """
    Feed a sample from an experiment.
    Returns two sets of bins. First one for the X, Yaw. Second for Y, Pitch.
    Data will be centered on 0, and divided into bins of size degs
    """
    yaws=scatterSample(sample)[0]
    pitchs=scatterSample(sample)[1]
    rolls=scatterSample(sample)[2]
    medYaw=np.median(yaws)
    medPitch=np.median(pitchs)
    medRoll=np.median(rolls)
    n=0
    while n< len(yaws):
        try:
         yaws[n]=yaws[n]-medYaw
         pitchs[n]=pitchs[n]-medPitch
         rolls[n]=rolls[n]-medRoll
        except:
            print('something weird happened with length')
        n=n+1

    twoBins=[bins(yaws, 15), bins(pitchs, 15), bins(rolls, 15)]
    return(twoBins)
    #okay, so take a value from yaws, now centered on 0
    #divide by 15, take int, e.g. yaw 14 returns 0, yaw 15->29 returns 1
    #increase count of bin[value from above division] by 1
    #repeat with pitch




def bins(measurements, degs):
    """
    takes a list of values
    Counts them in bins
    such that a value is put increases the count of a bin of int(value/degs)
    """
   # print(measurements)
    thisBin = {}
    for measure in measurements:
        #print(measure)
        binz = int(round(measure / degs))
        if bin in thisBin.keys():
            thisBin[binz].append(measure)
        else:
            thisBin[binz] = [measure]
    return (thisBin)


def addToBins(dicty, measurements, degs):
    """
    Takes a pair of dictionarys created by bins, and a second sample
    adds measurements from that sample to the bins
    returns the bins as a pair, as binning does.

    """
    print("Adding to Bin")
    print(measurements)
    yaws = scatterSample(measurements)[0]
    pitchs = scatterSample(measurements)[1]
    rolls = scatterSample(measurements)[2]
    #print(yaws)
    medYaw = np.median(yaws)
    medPitch = np.median(pitchs)
    medRoll = np.median(rolls)
    n = 0
    while n < len(yaws):
        #print(yaws[n])
        yaws[n] = yaws[n] - medYaw
        #print(yaws[n])
        pitchs[n] = pitchs[n] - medPitch
        rolls[n] = rolls[n] - medRoll
        n = n + 1
    for measure in yaws:
        binz= int(round(measure/degs))
        if binz in dicty[0].keys():
            dicty[0][binz].append(measure)
        else:
            dicty[0][binz]=[measure]
    for measure in pitchs:
        binz = int(round(measure/degs))
        if binz in dicty[1].keys():
            dicty[1][binz].append(measure)
        else:
            dicty[1][binz]=[measure]
    for measure in rolls:
        binz = int(round (measure/degs))
        if binz in dicty[2].keys():
            dicty[2][binz].append(measure)
        else:

            dicty[2][binz]=[measure]
    return(dicty)




##data[0] is the 'goodSets'
##data[0][0] is A goodset
##these won't be deMirror'd or scattered
##


#datas=deMirror(data[0][0])

#binned=binning(datas,15)

#topYaws=[]
#topPis=[]

#for key in binned[0].keys():
#    topYaws.append(binned[0][key])

#for key in binned[1].keys():
#    topPis.append(binned[1][key])


#plot=figure()


#degs=[]
#for value in list(binned[0]):
#    degs.append(value * 15)
#plot.vbar(x=degs, top=topYaws, width=.9)

#show(plot)

#degs=[]
#for value in list(binned[1]):
#    degs.append(value * 15)

#plot=figure()
#plot.vbar(x=degs, top=topPis, width=10)
#plot.title(arr.name +' Pitch values')
#show(plot)


###########
#Next step, now that addToBins is here (the above seems to work for a single sample)

#datas=data[0]

def summarizeYawPitchRoll(exper):
    """
    Take an experiment
    Normalize the data
    Subsample the data
    Bin the subsample results
    Return a list of bins from the subsamples
    Result type?
    :param exper:
    :return:
    """
    qCE=exper.quadCorrect(180)
    qCETB=qCE.topAndBottom()
    datas=chunkify(qCETB)
    data=datas[0]

    binned={}

    for subSample in data:
        #print(subSample)
        dM=deMirror(subSample)
        if binned=={}:
            binned=binning(dM,15)
        else:
            #print("Printing the demirrored subsample)")
            #print(dM)
            binned=addToBins(binned, dM,15)
    return(binned)




class Result(object):
    _filePath = None
    _day = None
    _worker = None
    _task = None
    _segment = None
    _hand = None
    _yaw = None
    _pitch = None
    _roll = None

    def __init__(self, exper = None):
        nameSplit=exper.name.split('_')
        self._day=nameSplit[0]
        self._task=nameSplit[2]
        self._worker=nameSplit[3]
        self._segment=nameSplit[4]
        self._hand=nameSplit[5]
        pathing=self._day + "\\" + self._task + "\\" + self._worker+"\\"+self._segment+"\\"+self._hand
        self._filePath=pathing
        summary=summarizeYawPitchRoll(exper)
        self._yaw=summary[0]
        self._pitch=summary[1]
        self._roll=summary[2]

    def printer(self):
        yawBins=list(self._yaw)
        yawCounts=[]
        degs=[]
        for bin in yawBins:
            count=len(self._yaw[bin])
            yawCounts.append(count)
            degs.append(bin*15)
        plot=figure()
        outLoc="C:\\Users\\Jacob\\Documents\\Data_Analytics\\Printer\\"+self._day+"\\"+self._task+"\\"+self._worker
        if not os.path.exists(outLoc):
            os.makedirs(outLoc)
        title=self._day+ " " + self._task+ " " + self._worker+ " " + self._segment+ " " + self._hand+ " "  + " yaw"
        plot.vbar(x=degs, top=yawCounts, width=10)
        plot.title.text=title
        plot.title.align="center"
        output_file(outLoc+"\\"+title.replace(" ", "_")+".html")
        show(plot)
        outCSV=outLoc+"\\" + title.replace(" ", "_") + ".csv"
        with open(outCSV, 'w') as csvfile:
            writer = csv.DictWriter(csvfile, self._yaw.keys())
            writer.writeheader()
            writer.writerow(self._yaw)
        pitchBins=list(self._pitch)
        pitchCounts=[]
        degs=[]
        for bin in pitchBins:
            count=len(self._pitch[bin])
            pitchCounts.append(count)
            degs.append(bin*15)
        plot=figure()
        outLoc="C:\\Users\\Jacob\\Documents\\Data_Analytics\\Printer\\"+self._day+"\\"+self._task+"\\"+self._worker
        if not os.path.exists(outLoc):
            os.makedirs(outLoc)
        title=self._day+ " " + self._task+ " " + self._worker+ " " + self._segment+ " " + self._hand+ " "  + " pitch"
        plot.vbar(x=degs, top=pitchCounts, width=10)
        plot.title.text=title
        plot.title.align="center"
        output_file(outLoc+"\\"+title.replace(" ", "_")+".html")
        show(plot)
        outCSV=outLoc+"\\" + title.replace(" ", "_") + ".csv"
        with open(outCSV, 'w') as csvfile:
            writer = csv.DictWriter(csvfile, self._pitch.keys())
            writer.writeheader()
            writer.writerow(self._pitch)

        rollBins = list(self._roll)
        rollCounts = []
        degs = []
        for bin in rollBins:
            count = len(self._roll[bin])
            rollCounts.append(count)
            degs.append(bin * 15)
        plot = figure()
        outLoc="C:\\Users\\Jacob\\Documents\\Data_Analytics\\Printer\\"+self._day+"\\"+self._task+"\\"+self._worker
        if not os.path.exists(outLoc):
            os.makedirs(outLoc)
        title = self._day + " " + self._task + " " + self._worker + " " + self._segment + " " + self._hand + " " + " roll"
        plot.vbar(x=degs, top=rollCounts, width=10)
        plot.title.text = title
        plot.title.align = "center"
        output_file(outLoc + "\\" + title.replace(" ", "_") + ".html")
        show(plot)
        outCSV = outLoc + "\\" + title.replace(" ", "_") + ".csv"
        with open(outCSV, 'w') as csvfile:
            writer = csv.DictWriter(csvfile, self._roll.keys())
            writer.writeheader()
            writer.writerow(self._roll)

    def printWeights(self):
        yawBins = list(self._yaw)
        yawCounts = []
        degs = []
        for bin in yawBins:
            count = len(self._yaw[bin])
            yawCounts.append(count)
            degs.append(bin * 15)
        plot = figure()
        outLoc = "C:\\Users\\Jacob\\Documents\\Data_Analytics\\Printer\\" + self._day + "\\" + self._task + "\\" + self._worker
        if not os.path.exists(outLoc):
            os.makedirs(outLoc)
        title = self._day + " " + self._task + " " + self._worker + " " + self._segment + " " + self._hand + " " + " yaw"
        plot.vbar(x=degs, top=yawCounts, width=10)
        plot.title.text = title
        plot.title.align = "center"
        output_file(outLoc + "\\" + title.replace(" ", "_") + ".html")
        show(plot)
        outCSV = outLoc + "\\" + title.replace(" ", "_") + ".csv"
        with open(outCSV, 'w') as csvfile:
                writer = csv.DictWriter(csvfile, self._yaw.keys())
                writer.writeheader()
                writer.writerow(self._yaw)
        pitchBins = list(self._pitch)
        pitchCounts = []
        degs = []
        for bin in pitchBins:
            count = len(self._pitch[bin])
            pitchCounts.append(count)
            degs.append(bin * 15)
        plot = figure()
        outLoc = "C:\\Users\\Jacob\\Documents\\Data_Analytics\\Printer\\" + self._day + "\\" + self._task + "\\" + self._worker
        if not os.path.exists(outLoc):
            os.makedirs(outLoc)
        title = self._day + " " + self._task + " " + self._worker + " " + self._segment + " " + self._hand + " " + " pitch"
        plot.vbar(x=degs, top=pitchCounts, width=10)
        plot.title.text = title
        plot.title.align = "center"
        output_file(outLoc + "\\" + title.replace(" ", "_") + ".html")
        show(plot)
        outCSV = outLoc + "\\" + title.replace(" ", "_") + ".csv"
        with open(outCSV, 'w') as csvfile:
            writer = csv.DictWriter(csvfile, self._pitch.keys())
            writer.writeheader()
            writer.writerow(self._pitch)

        rollBins = list(self._roll)
        rollCounts = []
        degs = []
        for bin in rollBins:
            count = len(self._roll[bin])
            rollCounts.append(count)
            degs.append(bin * 15)
        plot = figure()
        outLoc = "C:\\Users\\Jacob\\Documents\\Data_Analytics\\Printer\\" + self._day + "\\" + self._task + "\\" + self._worker
        if not os.path.exists(outLoc):
            os.makedirs(outLoc)
        title = self._day + " " + self._task + " " + self._worker + " " + self._segment + " " + self._hand + " " + " roll"
        plot.vbar(x=degs, top=rollCounts, width=10)
        plot.title.text = title
        plot.title.align = "center"
        output_file(outLoc + "\\" + title.replace(" ", "_") + ".html")
        show(plot)
        outCSV = outLoc + "\\" + title.replace(" ", "_") + ".csv"
        with open(outCSV, 'w') as csvfile:
            writer = csv.DictWriter(csvfile, self._roll.keys())
            writer.writeheader()
            writer.writerow(self._roll)
















                    #basepath_structured = r"C:\\Users\\Jacob\\Documents\\Trial_Data"
#exps = Experiments(basepath=basepath_structured, is_structured=True,
                   cache_path='cache_experiments.pkl')

#arr=exps._experiments[0]
#news=Result(arr)

#news.printer()



basepath_structured = r"C:\\Users\\Jacob\\Documents\\Trial_Data"
exps = Experiments(basepath=basepath_structured, is_structured=True,
                   cache_path='cache_experiments.pkl')


for experiment in exps._experiments:
    try:
       Result(experiment).printer()
    except:
      print("Exception occured while processing " experiment.name)


"""
So...
Going to try and pull all the data from all the membrane skinner tasks
Grab an experiment
Clean up the data (top/bottom on each experiment)
Drop the values into an array
Throw it at a PCA and see what we get
"""

outz=open("outz.csv",'w')
outz.write("Test")
outz.close()
import pandas as pd
def bigMatrix(experimental):
    """
    Takes an Experiments class
    Creates an array of values from all of the internal measurements
    :param experimental:
    :return:
    """
    #Might just write it out to a CSV file and load that as a numpy array?
    #That sounds easiest tbh
    outz=open("dummyoutfile.csv",'w')
    for expy in experimental:
        expy.topAndBottom()
        lenz=len(expy._yaw['hand'])#why not use this length?
        key=0
        while key < lenz :
            n=expy._yaw['hand'].keys()[key]
            #print(expy._yaw['hand'][n])
            outz.write(str(expy._yaw['hand'][n]) + ',' + str(expy._yaw['wrist'][n]) + ',' + str(expy._yaw['delta'][n]) + ',' + str(expy._pitch['hand'][n]) + ',' + str(expy._pitch['wrist'][n]) + ',' + str(expy._pitch['delta'][n]) + ',' + str(expy._roll['hand'][n]) + ',' + str(expy._roll['wrist'][n]) + ',' + str(expy._roll['delta'][n]) + ',' + str(expy._gx['hand'][n]) + ',' + str(expy._gx['wrist'][n]) + ',' + str(expy._gy['hand'][n]) + ',' + str(expy._gy['wrist'][n]) + ',' + str(expy._gz['hand'][n]) + ',' + str(expy._gz['wrist'][n]) + '\n')
            key=key+1
    outz.close()

    return(pd.read_csv('dummyoutfile.csv', sep = ','))











infP ="C:\\Users\\Jacob\\Documents\\Data_Analytics\\data_main_job.csv"
infArr=pd.read_csv(infP, sep=',')
infL=infArr.values
infL[:,11]=infL[:, 11] - np.mean(infL[:, 11])
infL[:,12]=infL[:, 12] - np.mean(infL[:, 12])
infL[:,13]=infL[:, 13] - np.mean(infL[:, 13])
infL[:,10]=infL[:, 10] - np.mean(infL[:, 10])
infL[:,22]=infL[:, 22] - np.mean(infL[:, 22])
infL[:,23]=infL[:, 23] - np.mean(infL[:, 23])
infL[:,24]=infL[:, 24] - np.mean(infL[:, 24])

slice1=[]
slice2=[]
slice3=[]
n=0
while n < len(infL[:, 11]):
    if (-40<infL[n, 11]<20) and (-60 < infL[n, 12]<30):
        slice1.append(infL[n, :])
    if (30<infL[n, 11] < 80) and (-60 < infL[n, 12] < 30):
        slice2.append(infL[n, :])
    if (20 < infL[n, 11] < 80) and (20 < infL[n, 12] < 60):
        slice3.append(infL[n, :])
    n=n+1

arrl = np.array(slice1)

deltaYaw = arrl[:, 10] - arrl[:, 22]
deltaPitch = arrl[:, 11] - arrl[:, 23]
deltaRoll = arrl[:, 12] - arrl[:, 24]
yawCounters = [0, 0, 0, 0, 0, 0, 0, 0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
for value in deltaYaw:
    bin = int((abs(value)) / 15)
    print(bin)
    yawCounters[bin] = yawCounters[bin] + 1

pawCounters = [0, 0, 0, 0, 0, 0, 0, 0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
for value in deltaPitch:
    bin = int((abs(value)) / 15)
    pawCounters[bin] = pawCounters[bin] + 1

rollCounters = [0, 0, 0, 0, 0, 0, 0, 0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
for value in deltaRoll:
    bin = int((abs(value)) / 15)
    rollCounters[bin] = rollCounters[bin] + 1

n = 0
score = 0
while n < len(rollCounters):
    yawscore = yawCounters[n] * n
    pawscore = pawCounters[n] * n
    rollscore = rollCounters[n] * n
    #print(pawscore)
    score = score + yawscore + pawscore + rollscore
    n = n + 1

arr2 = np.array(slice2)

deltaYaw2 = arr2[:, 10] - arr2[:, 22]
deltaPitch2 = arr2[:, 11] - arr2[:, 23]
deltaRoll2 = arr2[:, 12] - arr2[:, 24]
yawCounters2 = [0, 0, 0, 0, 0, 0, 0, 0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
for value in deltaYaw2:
    bin = int((abs(value)) / 15)
    yawCounters2[bin] = yawCounters2[bin] + 1

pawCounters2 = [0, 0, 0, 0, 0, 0, 0, 0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
for value in deltaPitch2:
    bin = int((abs(value)) / 15)
    pawCounters2[bin] = pawCounters2[bin] + 1

rollCounters2 = [0, 0, 0, 0, 0, 0, 0, 0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
for value in deltaRoll:
    bin = int((abs(value)) / 15)
    rollCounters2[bin] = rollCounters[bin] + 1

n = 0
score2 = 0
while n < len(rollCounters2):
    yawscore2 = yawCounters2[n] * n
    pawscore2 = pawCounters2[n] * n
    rollscore2 = rollCounters2[n] * n
    print(pawscore2)
    score2 = score2 + yawscore2 + pawscore2 + rollscore2
    n = n + 1

arr3 = np.array(slice3)

deltaYaw3 = arr3[:, 10] - arr3[:, 22]
deltaPitch3 = arr3[:, 11] - arr3[:, 23]
deltaRoll3 = arr3[:, 12] - arr3[:, 24]
yawCounters3 = [0, 0, 0, 0, 0, 0, 0, 0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
for value in deltaYaw3:
    bin = int((abs(value)) / 15)
    yawCounters3[bin] = yawCounters3[bin] + 1

pawCounters3 = [0, 0, 0, 0, 0, 0, 0, 0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
for value in deltaPitch3:
    bin = int((abs(value)) / 15)
    pawCounters[bin] = pawCounters[bin] + 1

rollCounters3 = [0, 0, 0, 0, 0, 0, 0, 0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
for value in deltaRoll3:
    bin = int((abs(value)) / 15)
    rollCounters3[bin] = rollCounters3[bin] + 1

n = 0
score3 = 0
while n < len(rollCounters3):
    yawscore = yawCounters3[n] * n
    pawscore = pawCounters3[n] * n
    rollscore = rollCounters3[n] * n
    score3 = score3 + yawscore + pawscore + rollscore
    n = n + 1



####getting speed scores (just using stdev)

basepath_structured = r"C:\\Users\\Jacob\\Documents\\Trial_Data"
exps = Experiments(basepath=basepath_structured, is_structured=True,
                   cache_path='cache_experiments.pkl')


def velcro(exp):
    '''exp needs to be of type experiment'''
    yawgradient=np.gradient(exp.yaw(delta=True))
    pitchgradient=np.gradient(exp.pitch(delta=True))
    rollgradient=np.gradient(exp.roll(delta=True))
    try:
        n=0
        yaw=[]
        pitch=[]
        roll=[]
        while n < len(yawgradient):
            if yawgradient[n] < 100:
                yaw.append(yawgradient[n])
            if pitchgradient[n] < 100:
                pitch.append(pitchgradient[n])
            if rollgradient[n] < 100:
                roll.append(rollgradient[n])
            n=n+1
    except:
        print("Failure occured while checking value " + str(n))
    return [np.std(yaw), np.std(pitch), np.std(roll), exp.name]

pyrStd=[]

for exp in exps._experiments:
    try:
        exp.topAndBottom()
        pyrStd.append(velcro(exp))
    except:
        print("Failure on " + exp.name)


####Subtasks for final bone
infP ="C:\\Users\\Jacob\\Documents\\Data_Analytics\\data_main_job_fb.csv"
infArr=pd.read_csv(infP, sep=',')
infL=infArr.values
infL[:,11]=infL[:, 11] - np.mean(infL[:, 11])
infL[:,12]=infL[:, 12] - np.mean(infL[:, 12])
infL[:,13]=infL[:, 13] - np.mean(infL[:, 13])
infL[:,10]=infL[:, 10] - np.mean(infL[:, 10])
infL[:,22]=infL[:, 22] - np.mean(infL[:, 22])
infL[:,23]=infL[:, 23] - np.mean(infL[:, 23])
infL[:,24]=infL[:, 24] - np.mean(infL[:, 24])

slice1=[]
slice2=[]
#slice3=[]

#(a) slice 1 final-boner left hand main job: (-60<data[:,11] <30.0)&(-30<data[:,12]<30.0)
#(b) slice 2 bone throwing using left hand: ( 30<data[:,11] <80.0)&(-30<data[:,12]<30.0)
n=0
while n < len(infL[:, 11]):
    if (-60<infL[n, 11]<30) and (-30 < infL[n, 12]<30):
        slice1.append(infL[n, :])
    if (30<infL[n, 11] < 80) and (-30 < infL[n, 12] < 30):
        slice2.append(infL[n, :])
    n=n+1

arrl = np.array(slice1)

deltaYaw = arrl[:, 10] - arrl[:, 22]
deltaPitch = arrl[:, 11] - arrl[:, 23]
deltaRoll = arrl[:, 12] - arrl[:, 24]
yawCounters = [0, 0, 0, 0, 0, 0, 0, 0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
for value in deltaYaw:
    bin = int((abs(value)) / 15)
    print(bin)
    yawCounters[bin] = yawCounters[bin] + 1

pawCounters = [0, 0, 0, 0, 0, 0, 0, 0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
for value in deltaPitch:
    bin = int((abs(value)) / 15)
    pawCounters[bin] = pawCounters[bin] + 1

rollCounters = [0, 0, 0, 0, 0, 0, 0, 0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
for value in deltaRoll:
    bin = int((abs(value)) / 15)
    rollCounters[bin] = rollCounters[bin] + 1

n = 0
score = 0
while n < len(rollCounters):
    yawscore = yawCounters[n] * n
    pawscore = pawCounters[n] * n
    rollscore = rollCounters[n] * n
    #print(pawscore)
    score = score + yawscore + pawscore + rollscore
    n = n + 1

arr2 = np.array(slice2)

deltaYaw2 = arr2[:, 10] - arr2[:, 22]
deltaPitch2 = arr2[:, 11] - arr2[:, 23]
deltaRoll2 = arr2[:, 12] - arr2[:, 24]
yawCounters2 = [0, 0, 0, 0, 0, 0, 0, 0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
for value in deltaYaw2:
    bin = int((abs(value)) / 15)
    yawCounters2[bin] = yawCounters2[bin] + 1

pawCounters2 = [0, 0, 0, 0, 0, 0, 0, 0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
for value in deltaPitch2:
    bin = int((abs(value)) / 15)
    pawCounters2[bin] = pawCounters2[bin] + 1

rollCounters2 = [0, 0, 0, 0, 0, 0, 0, 0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
for value in deltaRoll2:
    bin = int((abs(value)) / 15)
    rollCounters2[bin] = rollCounters2[bin] + 1

n = 0
score2 = 0
while n < len(rollCounters2):
    yawscore2 = yawCounters2[n] * n
    pawscore2 = pawCounters2[n] * n
    rollscore2 = rollCounters2[n] * n
    print(pawscore2)
    score2 = score2 + yawscore2 + pawscore2 + rollscore2
    n = n + 1

arr3 = np.array(slice3)

deltaYaw3 = arr3[:, 10] - arr3[:, 22]
deltaPitch3 = arr3[:, 11] - arr3[:, 23]
deltaRoll3 = arr3[:, 12] - arr3[:, 24]
yawCounters3 = [0, 0, 0, 0, 0, 0, 0, 0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
for value in deltaYaw3:
    bin = int((abs(value)) / 15)
    yawCounters3[bin] = yawCounters3[bin] + 1

pawCounters3 = [0, 0, 0, 0, 0, 0, 0, 0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
for value in deltaPitch3:
    bin = int((abs(value)) / 15)
    pawCounters[bin] = pawCounters[bin] + 1

rollCounters3 = [0, 0, 0, 0, 0, 0, 0, 0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
for value in deltaRoll3:
    bin = int((abs(value)) / 15)
    rollCounters3[bin] = rollCounters3[bin] + 1

n = 0
score3 = 0
while n < len(rollCounters3):
    yawscore = yawCounters3[n] * n
    pawscore = pawCounters3[n] * n
    rollscore = rollCounters3[n] * n
    score3 = score3 + yawscore + pawscore + rollscore
    n = n + 1


###Metrics class 5-29-19
import os
import matplotlib.pyplot as plt
import numpy as np
os.sys.path.append('C:\\Users\\Jacob\\Documents\\Data_Analytics\\Analytics')
import experiment
import events
basepath_unstruct = r"C:\\Users\\Jacob\\Documents\\ergo"
fileList=["C:\\Users\\Jacob\Documents\\ergo\\1_Right.csv", "C:\\Users\\Jacob\Documents\\ergo\\2_Right.csv","C:\\Users\\Jacob\Documents\\ergo\\3_Right.csv","C:\\Users\\Jacob\Documents\\ergo\\4_Right.csv","C:\\Users\\Jacob\Documents\\ergo\\5_Right.csv","C:\\Users\\Jacob\Documents\\ergo\\6_Right.csv","C:\\Users\\Jacob\Documents\\ergo\\7_Right.csv","C:\\Users\\Jacob\Documents\\ergo\\8_Right.csv","C:\\Users\\Jacob\Documents\\ergo\\9_Right.csv","C:\\Users\\Jacob\Documents\\ergo\\10_Right.csv","C:\\Users\\Jacob\Documents\\ergo\\11_Right.csv","C:\\Users\\Jacob\Documents\\ergo\\12_Right.csv"]
exps = experiment.Experiments(basepath = basepath_unstruct, list_of_filenames=fileList, cache_path = 'eg')



basepath_structured = r"C:\\Users\\Jacob\\Documents\\Trial_Data"
exps = experiment.Experiments(basepath=basepath_structured, is_structured=True,
                 cache_path='cache_QC_Automated.pkl')

arr = exps._experiments[119]
#meaty = events.Metrics(arr)

basepath_unstruct = r"C:\\Users\\Jacob\\Documents\\ergo"
exps = experiment.Experiments(basepath=basepath_structured, is_structured=True,
                 cache_path='cache_ergo.pkl')
#Trying to find reach up in left hand membrane skinner pitch values



meaty=events.Metrics(exps._experiments[118])
pW=meaty._pitches['wrist']
pH=meaty._pitches['hand']
highPW=[]
highPH=[]
n=0
x=[]
while n<len(pW):
    if pW[n]>20:
        highPW.append(pW[n])
    else:
        highPW.append(0)
    if pH[n]>20:
        highPH.append(pH[n])
    else:
        highPH.append(0)
    x.append(n)
    n=n+1


plt.scatter(x,highPH)
plt.scatter(x,highPW)



meaty=events.Metrics(exps._experiments[119])
yW=meaty._yaws['wrist']
yH=meaty._yaws['hand']
highYW=[]
highYH=[]
n=0
x=[]
while n<len(yW):
    if yW[n]>20:
        highYW.append(yW[n])
    else:
        highYW.append(0)
    if yH[n]>20:
        highYH.append(yH[n])
    else:
        highYH.append(0)
    x.append(n)
    n=n+1


plt.scatter(x,highYH)
plt.scatter(x,highYW)


###Metrics class 5-29-19
import os
import matplotlib.pyplot as plt
import numpy as np
os.sys.path.append('C:\\Users\\Jacob\\Documents\\Data_Analytics\\Analytics')
import experiment
import events
basepath_unstruct = r"C:\\Users\\Jacob\\Documents\\ergo"
fileList=["C:\\Users\\Jacob\Documents\\ergo\\1_Right.csv", "C:\\Users\\Jacob\Documents\\ergo\\2_Right.csv","C:\\Users\\Jacob\Documents\\ergo\\3_Right.csv","C:\\Users\\Jacob\Documents\\ergo\\4_Right.csv","C:\\Users\\Jacob\Documents\\ergo\\5_Right.csv","C:\\Users\\Jacob\Documents\\ergo\\6_Right.csv","C:\\Users\\Jacob\Documents\\ergo\\7_Right.csv","C:\\Users\\Jacob\Documents\\ergo\\8_Right.csv","C:\\Users\\Jacob\Documents\\ergo\\9_Right.csv","C:\\Users\\Jacob\Documents\\ergo\\10_Right.csv","C:\\Users\\Jacob\Documents\\ergo\\11_Right.csv","C:\\Users\\Jacob\Documents\\ergo\\12_Right.csv"]
z=experiment.Experiment(path=fileList[4])