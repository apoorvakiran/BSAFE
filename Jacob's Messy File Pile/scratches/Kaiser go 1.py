
import os
import matplotlib.pyplot as plt
import numpy as np
import experiment

Kaiser = r"C:\\Users\\Jacob\\Documents\\Data_Analytics\\Quick Analytic demo\\kaiser_data (1).csv"


kExper = experiment.Experiment(name = "name_name_name", path = Kaiser)
####HAD TO MODIFY EXPERIMENT, THIS DOESN'T LOAD PROPERLY BECAUSE IT IS ALL HIGH STDev! Modified TopandBottom function
####Normally this wouldn't be an issue, but since we've already pre-truncated the data to an active period it is
####Gotta build something in to deal with this.


z= metrics.Metrics(kExper)
trying = output.Output(typ='http', mets = z, auth = 'Bearer eyJhbGciOiJIUzI1NiJ9.eyJ1c2VyX2lkIjoxfQ.x2T_qKsO8gSOz2WHLCyFzuf059L2NeH6TtdKX783ZHs', outSpot = 'https://api-staging.iteratetech.com/api/v1/safety_scores', macID = 'F6:12:3D:BD:DE:44')

import TheHits

trying = TheHits.theHits(kExper, 20, 15, 20)


import metrics
metty = metrics.Metrics(kExper)

speed_pitch_score=5.5&speed_yaw_score=5.5&speed_roll_score=5.5&normalized_speed_pitch_score=5.5&normalized_speed_yaw_score=5.5&normalized_speed_roll_score=5.5&speed_score=5.5&strain_pitch_score=5.5&strain_yaw_score=5.5&strain_roll_score=5.5&strain_score=5.5&posture_score=5.5&safety_score=5.5

import requests

payload_dict = {'mac':'F6:12:3D:BD:DE:44', 'speed_pitch_score': 5.5, 'speed_roll_score': 5.5, 'speed_yaw_score':5.5,
                'normalized_speed_pitch_score': 5.5, 'normalized_speed_yaw_score': 5.5,
                'normalized_speed_roll_score':5.5, 'speed_score': 5.5, 'strain_pitch_score': 5.5,
                'strain_yaw_score': 5.5, 'strain_roll_score': 5.5, 'strain_score':5.5, 'posture_score': 5.5,
                'safety_score': 5.5, 'analyzed_at': '2019-08-14+21%3A11%3A14+UTC'}

headers = {'Authorization': 'Bearer eyJhbGciOiJIUzI1NiJ9.eyJ1c2VyX2lkIjoxfQ.x2T_qKsO8gSOz2WHLCyFzuf059L2NeH6TtdKX783ZHs'}
resp = requests.post('https://api-staging.iteratetech.com/api/v1/safety_scores', headers=headers, data=payload_dict)