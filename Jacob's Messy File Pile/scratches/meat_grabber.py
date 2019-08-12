#Working on the eventFinder function, will be using to track meat grabbing cycles in membrane skinner
import numpy as np
import os
import matplotlib.pyplot as plt
import numpy as np
os.sys.path.append('C:\\Users\\Jacob\\Documents\\Data_Analytics\\Analytics')
import experiment
import events

basepath_structured = r"C:\Users\Jacob\Documents\Client-Data\Tyson\Pilot"
exps = experiment.Experiments(basepath=basepath_structured, is_structured=True,
                 cache_path='Tyson_post2.pkl')


def eventFinder(exper, angle):
    """Feed an experiment object, return a list of individual event objects.
    Assumption: Values in the experiment are held in order of timing."""
    #So an event is a period of time where one or more delta values is greater than angle
    yaws = exper._yaws
    rolls = exper._rolls
    pitches = exper._pitches
    exper = exper.name
    events = []
    range = None
    n = 0
    eventNumber = -1
    inEvent  =  False
    while n < maxSize:
        if inEvent:
            if abs(yaws[n]) > angle or abs(pitches[n]) > angle or abs(rolls[n]) > angle:

                events[eventNumber]['pitch'].append(pitches[n])
                events[eventNumber]['yaws'].append(yaws[n])
                events[eventNumber]['rolls'].append(rolls[n])
            else:
                 inEvent=False
        else:
            if abs(yaws[n]) > angle or abs(pitches[n]) > angle or abs(rolls[n]) > angle:
                inEvent=True
                eventNumber=eventNumber+1
                events.append({})
                events[eventNumber]['pitch'] = []
                events[eventNumber]['pitch'].append(pitches[n])
                events[eventNumber]['yaws'] = []
                events[eventNumber]['yaws'].append(yaws[n])
                events[eventNumber]['rolls'] = []
                events[eventNumber]['rolls'].append(rolls[n])
        n = n+1
    eventList=[]
    for item in events:
        pitch = item['pitch']
        yaw = item['yaws']
        roll = item['rolls']
        newEvent = Event(pitch, yaw, roll, exper)
        eventList.append(newEvent)
    return eventList


def rangeFinder (exper):
    n=0
    validz=[]
    yawz=exper._yaw['wrist']
    while n+119<len(yawz):
        n2 = n+119
        standy=np.std(yawz[n:n2])
        if standy > 10:
            validz.append(yawz[n:n2])
        else:
            if len(validz) >0 or validz[-1] == ['Break']:
                pass
            else:
                validz.append(['Break'])
        n=n+120
    return validz


def contWork(list):
    """Takes a list of lists created by rangeFinder, and combines working periods together into single continuous
    entities, broken up by breaks"""
    contiguous=[]
    segment=[]
    for value in list:
        if value=='Break':
            print('found break')
            contiguous.append(segment)
            segment=[]
        else:
            #print(segment)
            #print(value)
            segment=segment+[value]
    return contiguous

cont=contWork(z)
###########Quick scripting...
import os
import matplotlib.pyplot as plt
import numpy as np
os.sys.path.append('C:\\Users\\Jacob\\Documents\\Data_Analytics\\Analytics')
os.sys.path.append('C:\\Users\\Jacob\\Documents\\Data_Analytics\\Analytics')
import experiment

basepath_structured = r"C:\\Users\\Jacob\\Documents\\Trial_Data"
exps = experiment.Experiments(basepath=basepath_structured, is_structured=True,
                 cache_path='cache_QC_Automated.pkl')



memRight=[]
for value in exps._experiments:
    if (value._meta_data['hand'] == 'Right') and (value._meta_data['task_name'] == 'membraneskinner'):
        memRight.append(value)
    else:
        pass



##Okay...
#list of observations
#Lets look at 2 minute periods...

def meatGrabbed(list):
    """Just give it a list of yaw values (not Delta), will spit out a list of number of meat grabs in 2 minute periods"""
    grabs=[]
    entry=0
    n=0
    over30=0
    while n < len(list):
        counts=0
        entry = entry + 1
        while n < entry*1200: #2 minute segments here
            if n == len(list)-1:
                return grabs
            if over30>0:  #have seen a value over 30
                if list[n]>30: #value is still over 30
                    n=n+1 #increment where we're looking
                    over30=over30+1 #adding 1 to the duration of the reach event
                else:
                    #So we are no longer in an over30 stretch
                    if over30>2: #more than a single measurement has been seen, so we'll up counts
                        counts=counts+1
                        print(counts)
                    over30=0 #setting it to 0
                    n=n+1
            else: #haven't seen a value over 30 yet
                if list[n]>30: #ohshi, here we go
                    over30=1
                n=n+1
        grabs.append(counts)
    return grabs




grabby=meatGrabbed(yex2.yaw(loc='wrist')-np.mean(yex2.yaw(loc='wrist')))

hister=[]
for value in grabby:
    if value > 0:
        hister.append(value)


