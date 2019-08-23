import os
import csv

from Analytics.StructuredData import StructuredDataStatic

basepath_structured = r"C:\\Users\\Jacob\\Documents\\Trial_Data"
exps = StructuredDataStatic.Experiments(basepath=basepath_structured, is_structured=True,
                                        cache_path='cache_experiments.pkl')

arr = exps._experiments[0]
meaty = events.Metrics(arr)

#arr.quadCorrect(180)
#arr.topAndBottom()
from bokeh.plotting import figure, output_file, show

#output_file('default.html')


from random import randint
import numpy as np


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
  areaSet=[]
  n=0

  while n<len(someValues[0]):
   if (safeYawmin<=yaws[n]<=safeYawmax and safePitchmin<=pitchs[n]<=safePitchmax and rollMin<rolls[n]<rollMax):
     lowRisk.append([yaws[n],pitchs[n],rolls[n]])
     areaSet.append([yaws[n], pitchs[n]])
   else:
     higherRisk.append([yaws[n],pitchs[n],rolls[n]])
   n=n+1
  return([lowRisk, higherRisk, areaSet])

def chunkify(exper):
 chunkySet =[]
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
         print(np.std(thisYaSample))
         if (np.std(thisYaSample)>10 and np.std(thisPiSample)>10 and np.std(thisRollSample) > 10):
          groupz = groupMaker([np.array(thisYaSample), np.array(thisPiSample), np.array(thisRollSample)], 2)
          goodSets.append(groupz[0])
          badSets.append(groupz[1])
          chunkySet.append(deMirrorTwo(groupz[2]))
     n = n + 1
 #areaCalc=[minYa, maxYa, minPi, maxPi, minRo, maxRo]
 return([goodSets, badSets, chunkySet])


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

def deMirrorTwo(sampleset):
    #print('DMTWO')
    exes=[]
    for pnt in sampleset:
        exes.append(pnt[0])
    center=np.mean(exes)
    #print(center)
    newSet=[]
    for pnt in sampleset:
        #print(pnt)
        #print(pnt)
        if pnt[0]>center:
            exxDif=center-pnt[0]
            #distance from the middle point
            newExx=center-np.absolute(exxDif)
            newPnt=[newExx,pnt[1]]
            #print(newExx)
            newSet.append(newPnt)
            #print(newPnt)
        else:
            newSet.append([pnt[0],pnt[1]])
            #print(pnt)
    #print(newSet)
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
 #newSizes=[]
 #check=chunks[0]
 #n=0
 #while n < len(check):
#     check[n]=deMirror(check[n])
#     n=n+1
# for set in check:
#   newSizes.append(ConvexHull(set).area)
# return(newSizes)


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
   # print("Adding to Bin")
    #print(measurements)
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
    exper.quadCorrect(180)
    exper.topAndBottom()
    chunks=chunkify(exper)
    data=chunks[0]
    area=chunks[2]
    print(chunks)
    binned={}
    for subSample in data:
        print(subSample)
        dM=deMirror(subSample)
        if binned=={}:
            binned=binning(dM,15)
        else:
            #print("Printing the demirrored subsample)")
            #print(dM)
            binned=addToBins(binned, dM,15)
    return(binned, area)




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
    _area = None

    def __init__(self, exper = None):
        nameSplit = exper.name.split('_')
        self._day = nameSplit[0]
        self._task = nameSplit[2]
        self._worker = nameSplit[3]
        self._segment = nameSplit[4]
        self._hand = nameSplit[5]
        pathing = self._day + "\\" + self._task + "\\" + self._worker+"\\"+self._segment+"\\"+self._hand
        self._filePath = pathing
        summ = summarizeYawPitchRoll(exper)
        summary = summ[0]
        areaSize=summ[1]
        self._area = areaSize
        #print(summary)
        self._yaw = summary[0]
        self._pitch = summary[1]
        self._roll = summary[2]

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

    def areaAndMetric(self):
       # print(self._area)
        areaValue=self._area
        binnedYaw=self._yaw
        binnedPitch=self._pitch
        binnedRoll=self._roll
        yawWeights=[]
        pitchWeights=[]
        rollWeights=[]
        for key in list(binnedYaw.keys()):
            weight=abs(key)
            counts=len(binnedYaw[key])
            weighty=weight*counts
            yawWeights.append(weighty)
        for key in list(binnedPitch.keys()):
            weight=abs(key)
            counts=len(binnedPitch[key])
            weighty=weight*counts
            pitchWeights.append(weighty)
        for key in list(binnedRoll.keys()):
            weight=abs(key)
            counts=len(binnedRoll[key])
            weighty=weight*counts
            rollWeights.append(weighty)
        title = self._day + " " + self._task + " " + self._worker + " " + self._segment + " " + self._hand
        returnable=[title]
        returnable.append(np.mean(pitchWeights))
        returnable.append(np.mean(yawWeights))
        returnable.append(np.mean(rollWeights))
        returnable.append(areaValue)
        return(returnable)
















#basepath_structured = r"C:\\Users\\Jacob\\Documents\\Trial_Data"
#exps = Experiments(basepath=basepath_structured, is_structured=True,
#                   cache_path='cache_experiments.pkl')

#arr=exps._experiments[0]
#news=Result(arr)

#news.printer()



basepath_structured = r"C:\\Users\\Jacob\\Documents\\Trial_Data"
exps = Experiments(basepath=basepath_structured, is_structured=True,
                   cache_path='cache_experiments.pkl')

arr=Result(exps._experiments[0])
quez=arr.areaAndMetric()


toPrint=[]

writer=open("C:\\Users\\Jacob\\Documents\\Data_Analytics\\WithTruncate.csv", 'w')
for experiment in exps._experiments:

    try:
    #print(experiment.name)
     arr=Result(experiment)
     printables=arr.areaAndMetric()
     writer.write(printables[0] + ", " + str(printables[1]) + ", " + str(printables[2]) + ", " + str(printables[3])+ ", " + str(printables[4])+"\n" )
    except:
        print("failure on " + str(experiment.name))
       # toPrint.append(experiment.name)




writer=open("C:\\Users\\Jacob\\Documents\\Data_Analytics\\MetricTest.csv", 'w')
for entry in toPrint:
    for item in entry:
        writer.write(str(item))
        writer.write(", ")
    writer.write('\n')

test="C:\\Users\\Jacob\\Documents\\Trial_Data\\Monday\\blade bone\\jonathan\\Monday_TeamB_BladeBone_Jonathan_Segment2_Left.csv"
expy=Experiment(test)

target="C:\\Users\\Jacob\\Documents\\Trial_Data\\Monday\\blade bone\\jonathan\\Monday_TeamB_BladeBone_Jonathan_Segment2_left.csv"
expy=Experiment(target, name="Monday_TeamB_BladeBone_Jonathan_Segment2_left.csv")



target="C:\\Users\\Jacob\\Documents\\Trial_Data\\Monday\\blade bone\\jonathan\\Monday_TeamB_BladeBone_Jonathan_Segment1_left.csv"
expy=Experiment(target, name="Monday_TeamB_BladeBone_Jonathan_Segment1_left.csv")
arr=Result(expy)
printables=arr.areaAndMetric()
writer.write(printables[0] + ", " + str(printables[1]) + ", " + str(printables[2]) + ", " + str(printables[3])+"\n")