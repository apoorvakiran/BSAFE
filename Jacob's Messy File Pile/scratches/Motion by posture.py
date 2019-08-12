

#So have an experiments object exps
#Want to pull out scores for workers (metrics) from each experiment
#So let's sort this by worker
import os
import matplotlib.pyplot as plt
import numpy as np
os.sys.path.append('C:\\Users\\Jacob\\Documents\\Data_Analytics\\Analytics')
import experiment

basepath_structured = r"C:\\Users\\Jacob\\Documents\\Trial_Data"
exps = experiment.Experiments(basepath=basepath_structured, is_structured=True,
                 cache_path='Tyson_newPost.pkl')

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


#Lets make a list of values for workers...
#Max score?
#Max score
#¯\_(ツ)_/¯
listable=[]
scores={} #will hold [worker]: [Motion, Posture], where motion will be a single value taken from the max of all experiments

for worker in meteors['MembraneSkinner']:
    for exp in meteors['MembraneSkinner'][worker]:
        if worker not in scores.keys():
            scores[worker]=[0,0]
        posty=exp._metrics._posture
        mots=exp._metrics._motion
        scores[worker][0]=max(scores[worker][0], mots[3])
        scores[worker][1]=max(scores[worker][1], posty)



bbscores={} #will hold [worker]: [Motion, Posture], where motion will be a single value taken from the max of all experiments

for worker in meteors['BladeBone']:
    for exp in meteors['BladeBone'][worker]:
        if worker not in scores.keys():
            bbscores[worker]=[0,0]
        posty=exp._metrics._posture
        mots=exp._metrics._motion
        bbscores[worker][0]=max(bbscores[worker][0], mots[3])
        bbscores[worker][1]=max(bbscores[worker][1], posty)


fbscores={} #will hold [worker]: [Motion, Posture], where motion will be a single value taken from the max of all experiments

for worker in meteors['FinalBone']:
    for exp in meteors['FinalBone'][worker]:
        if worker not in scores.keys():
            fbscores[worker]=[0,0]
        posty=exp._metrics._posture
        mots=exp._metrics._motion
        fbscores[worker][0]=max(fbscores[worker][0], mots[3])
        fbscores[worker][1]=max(fbscores[worker][1], posty)

