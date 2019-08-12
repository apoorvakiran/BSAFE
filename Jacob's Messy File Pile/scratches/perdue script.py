
import os
import matplotlib.pyplot as plt
import numpy as np
os.sys.path.append('C:\\Users\\Jacob\\Documents\\Data_Analytics\\Analytics')
import experiment
import events



basepath_structured = r"C:\\Users\\Jacob\\Documents\\Client-Data\\Perdue\\Pilot"
exps = experiment.Experiments(basepath=basepath_structured, is_structured=True,
                 cache_path='pD-cache4.pkl')


for exp in exps._experiments:
    print(exp.name)
    print(exp._metrics._motion)
    print(exp._metrics._posture)
    print(exp._metrics._speed)


def printer(experiez, outfile):
    totalz=totaller(experiez)
    printed=open(outfile, 'w')
    printed.write('Day, Shift, Task, Worker, Segment, Hand, Motion - Pitch, Motion - Yaw, Motion - Roll, Motion, Posture, Speed - Pitch, Speed - Yaw, Speed - Roll')
    printed.write('\n')
    for key in totalz:
        #printed.write(key)
        #printed.write("\n")
        scores=[]
        for score in totalz[key]:
            scores.append(score)
        scores.sort(reverse=True)
        n=0
        summary=[0,0,0,0,0,0,0,0]
        while n < len(scores):
            for exp in totalz[key][scores[n]]:
                metric=exp._metrics
                motion=metric._motion
                summary[0]=summary[0]+motion[0]
                summary[1]=summary[1]+motion[1]
                summary[2]=summary[2]+motion[2]
                summary[3]=summary[3]+motion[3]
                post=metric._posture*7
                summary[4]=summary[4]+post
                speeds=metric._speed
                summary[5]=summary[5]+speeds[0]
                summary[6]=summary[6]+speeds[1]
                summary[7]=summary[7]+speeds[2]
                name=exp.name.replace('_', ', ')
                printed.write(name + ", " + str(motion[0]) + ", " + str(motion[1]) + ", " + str(motion[2]) + ", "
                                                 + str(motion[3]) + ", " + str(post) + ", " + str(speeds[0]) + ", " +
                                                 str(speeds[1]) + ", " + str(speeds[2]) + ", " + "\n")
            n=n+1
        summary[0] = np.mean(summary[0])/n
        summary[1] = np.mean(summary[1])/n
        summary[2] = np.mean(summary[2])/n
        summary[3] = np.mean(summary[3])/n
        summary[4] = np.mean(summary[4])/n
        summary[5] = np.mean(summary[5])/n
        summary[6] = np.mean(summary[6])/n
        summary[7] = np.mean(summary[7])/n
        #printed.write(",,,, ,, " + str(summary[0]) + ", " + str(summary[1]) + "," +
                   #   str(summary[2]) + ", " + str(summary[3]) + ", " + str(summary[4]) + ", " + str(summary[5]) +
                    #  ", " + str(summary[6]) + ", " + str(summary[7]) + "\n")
        #printed.write("\n")
    printed.close()








outfile = "Perdue_outfile_mk2.csv"

printer(exps, outfile)


def totaller(experiez):
    rankings={}
    for exp in experiez._experiments:
        name = exp.name.split('_')
        task = name[2]
        score=exp._metrics._motion[3]
        if task not in rankings:
            rankings[task]={}
            rankings[task][score]=[exp]
        else:
            if score not in rankings[task]:
                rankings[task][score]=[exp]
            else:
                rankings[task][score].append(exp)
    return rankings


