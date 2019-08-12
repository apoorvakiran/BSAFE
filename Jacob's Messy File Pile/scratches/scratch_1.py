#For some reason I can't load the Borgwarner data in

basepath_structured = r"C:\\Users\\Jacob\\Documents\\Data_Analytics\\Borgwarner"
exps = Experiments(basepath=basepath_structured, is_structured=True,
                   cache_path='bw_cache_experiments.pkl')
#
basepath_structured = r"C:\\Users\\Jacob\\Documents\\Trial_Data"
#exps = Experiments(basepath=basepath_structured, is_structured=True,
#                   cache_path='cache_experiments.pkl')


file1="C:\\Users\\Jacob\\Documents\\Data_Analytics\\Borgwarner\\Monday\\task\\worker\\Segment1_Right.csv"
file2="C:\\Users\\Jacob\\Documents\\Data_Analytics\\Borgwarner\\Monday\\task\\worker\\Segment2_Right.csv"
file3="C:\\Users\\Jacob\\Documents\\Data_Analytics\\Borgwarner\\Monday\\task\\worker\\Segment3_Right.csv"
file4="C:\\Users\\Jacob\\Documents\\Data_Analytics\\Borgwarner\\Monday\\task\\worker\\Segment4_Right.csv"
file5="C:\\Users\\Jacob\\Documents\\Data_Analytics\\Borgwarner\\Monday\\task\\worker\\Segment4_Right_new.csv"

exp1=Experiment(file1)
exp2=Experiment(file2)
exp3=Experiment(file3)
exp4=Experiment(file4)
exp5=Experiment(file5)

exp1._name="exp1_day_task_worker_segment_hand_dunno_trialanderror.csv"
exp2._name="exp2_day_task_worker_segment_hand_dunno_trialanderror.csv"
exp3._name="exp3_day_task_worker_segment_hand_dunno_trialanderror.csv"
exp4._name="exp4_day_task_worker_segment_hand_dunno_trialanderror.csv"
exp5._name="exp5_day_task_worker_segment_hand_dunno_trialanderror.csv"


chunky1=chunkify(exp1)
chunky2=chunkify(exp2)
chunky3=chunkify(exp3)
chunky4=chunkify(exp4)
chunky5=chunkify(exp5)

data1=chunky1[0]
data2=chunky2[0]
data3=chunky3[0]
data4=chunky4[0]
data5=chunky5[0]

bin1=binning(data[0],15)
for subz in data[1:]:
    bin1=addToBins(bin1, subz, 15)

bin2 = binning(data2[0], 15)
for subz in data2[1:]:
    bin2 = addToBins(bin2, subz, 15)

bin3 = binning(data3[0], 15)
for subz in data3[1:]:
    bin3 = addToBins(bin3, subz, 15)

bin4 = binning(data4[0], 15)
for subz in data4[1:]:
    bin4 = addToBins(bin4, subz, 15)


bin5 = binning(data5[0], 15)
for subz in data5[1:]:
    bin5 = addToBins(bin5, subz, 15)



def printer(binSet, name):
        yawBins=list(binSet[1])
        yawCounts=[]
        degs=[]
        for bin in yawBins:
            count=len(binSet[1][bin])
            yawCounts.append(count)
            degs.append(bin*15)
        plot=figure()
        outLoc="C:\\Users\\Jacob\\Documents\\Data_Analytics\\Printer\\"+name
        if not os.path.exists(outLoc):
            os.makedirs(outLoc)
        title=name+ " yaw"
        plot.vbar(x=degs, top=yawCounts, width=10)
        plot.title.text=title
        plot.title.align="center"
        output_file(outLoc+"\\"+title.replace(" ", "_")+".html")
        show(plot)
        outCSV=outLoc+"\\" + title.replace(" ", "_") + ".csv"
        with open(outCSV, 'w') as csvfile:
            writer = csv.DictWriter(csvfile, binSet[1].keys())
            writer.writeheader()
            writer.writerow(binSet[1])

        rollBins=list(binSet[2])
        rollCounts=[]
        degs=[]
        for bin in rollBins:
            count=len(binSet[2][bin])
            rollCounts.append(count)
            degs.append(bin*15)
        plot=figure()
        outLoc="C:\\Users\\Jacob\\Documents\\Data_Analytics\\Printer\\"+name
        if not os.path.exists(outLoc):
            os.makedirs(outLoc)
        title=name+ " roll"
        plot.vbar(x=degs, top=rollCounts, width=10)
        plot.title.text=title
        plot.title.align="center"
        output_file(outLoc+"\\"+title.replace(" ", "_")+".html")
        show(plot)
        outCSV=outLoc+"\\" + title.replace(" ", "_") + ".csv"
        with open(outCSV, 'w') as csvfile:
            writer = csv.DictWriter(csvfile, binSet[2].keys())
            writer.writeheader()
            writer.writerow(binSet[2])

        pitchBins=list(binSet[0])
        pitchCounts=[]
        degs=[]
        for bin in pitchBins:
            count=len(binSet[0][bin])
            pitchCounts.append(count)
            degs.append(bin*15)
        plot=figure()
        outLoc="C:\\Users\\Jacob\\Documents\\Data_Analytics\\Printer\\"+name
        if not os.path.exists(outLoc):
            os.makedirs(outLoc)
        title=name+ " pitch"
        plot.vbar(x=degs, top=pitchCounts, width=10)
        plot.title.text=title
        plot.title.align="center"
        output_file(outLoc+"\\"+title.replace(" ", "_")+".html")
        show(plot)
        outCSV=outLoc+"\\" + title.replace(" ", "_") + ".csv"
        with open(outCSV, 'w') as csvfile:
            writer = csv.DictWriter(csvfile, binSet[0].keys())
            writer.writeheader()
            writer.writerow(binSet[0])


printer(bin4, exp4.name)


import numpy as np

def areaAndMetric(bins, givenT):
    # print(self._area)
    binnedYaw = bins[0]
    binnedPitch = bins[1]
    binnedRoll = bins[2]
    yawWeights = []
    pitchWeights = []
    rollWeights = []
    for key in list(binnedYaw.keys()):
        weight = abs(key)
        counts = len(binnedYaw[key])
        weighty = weight * counts
        yawWeights.append(weighty)
    for key in list(binnedPitch.keys()):
        weight = abs(key)
        counts = len(binnedPitch[key])
        weighty = weight * counts
        pitchWeights.append(weighty)
    for key in list(binnedRoll.keys()):
        weight = abs(key)
        counts = len(binnedRoll[key])
        weighty = weight * counts
        rollWeights.append(weighty)
    title = givenT
    returnable = [title]
    returnable.append(np.mean(pitchWeights))
    returnable.append(np.mean(yawWeights))
    returnable.append(np.mean(rollWeights))
    return (returnable)



z4=areaAndMetric(bin4, "Segment 4 Scores")
z3=areaAndMetric(bin3, "Segment 3 Scores")
z2=areaAndMetric(bin2, "Segment 2 Scores")
z1=areaAndMetric(bin1, "Segment 1 Scores")
z5=areaAndMetric(bin5, "Segment 5 Scores")

writer=open("C:\\Users\\Jacob\\Documents\\Data_Analytics\\BWMetrics.csv", 'w')

writer.write(str(z1))
writer.write("\\n")
writer.write(str(z2))
writer.write(str("\\n"))
writer.write(str(z3))
writer.write("\\n")
writer.write(str(z4))
writer.write("\\n")
writer.write(str(z5))
writer.write("\\n")

writer.close()



#Okay, have those metrics out. Time for posture and speed scores
###THIS IS NOT HOW TO DO POSTURE OR SPEED###
deltaYaw=exp1.yaw(delta=True)
deltaYaw2=exp2.yaw(delta=True)
deltaYaw3=exp3.yaw(delta=True)
deltaYaw4=exp4.yaw(delta=True)
deltaYaw5=exp5.yaw(delta=True)
deltaPitch=exp1.pitch(delta=True)
deltaPitch2=exp2.pitch(delta=True)
deltaPitch3=exp3.pitch(delta=True)
deltaPitch4=exp4.pitch(delta=True)
deltaPitch5=exp5.pitch(delta=True)
deltaRoll5=exp5.roll(delta=True)
deltaRoll4=exp4.roll(delta=True)
deltaRoll3=exp3.roll(delta=True)
deltaRoll2=exp2.roll(delta=True)
deltaRoll=exp1.roll(delta=True)

#exp1
score=0
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


#exp1

def postScore(yaw, pitch, roll,safe):
    """Takes three lists of values, yaw pitch and roll, and calculates posture score
    as percent of time spent outside of a 'safe' posture"""
    totalVals=0
    unsafe=0
    for val in yaw:
        if val > safe:
            unsafe=unsafe+1
        totalVals=totalVals+1
    for val in pitch:
        if val > safe:
            unsafe=unsafe+1
        totalVals=totalVals+1
    for val in roll:
        if val > safe:
            unsafe = unsafe+1
        totalVals=totalVals+1
    return(unsafe/totalVals)

post1=postScore(exp1.yaw(delta=True), exp1.roll(delta=True), exp2.pitch(delta=True), 30)
post2=postScore(exp2.yaw(delta=True), exp2.roll(delta=True), exp2.pitch(delta=True), 30)
post3=postScore(exp3.yaw(delta=True), exp3.roll(delta=True), exp3.pitch(delta=True), 30)
post4=postScore(exp4.yaw(delta=True), exp4.roll(delta=True), exp4.pitch(delta=True), 40)
post5=postScore(exp5.yaw(delta=True), exp5.roll(delta=True), exp5.pitch(delta=True), 50)


#speed
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

speed1=velcro(exp1)
speed2=velcro(exp2)
speed3=velcro(exp3)
speed4=velcro(exp4)
speed5=velcro(exp5)
