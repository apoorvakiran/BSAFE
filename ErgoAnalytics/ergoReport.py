from datetime import datetime
import requests

__all__ = ['ErgoReport']


class ErgoReport (object):
    """Feed a metrics object and a desired output type (string, HTTP request, csv), receive an output"""
    _type = None
    _metrics = None
    _authorization = None
    _locationOut = None
    _id = None
    _sent = None

    def __init__(self, typ=None, mets=None, auth=None, outSpot=None, macID=None):
        self._type = typ
        self._metrics = mets
        self._authorization = auth
        self._locationOut = outSpot
        self._id = macID
        payload = self.htOut()
        if typ == 'http':
            try:
                headers = {
                    'Authorization': self._authorization}
                self._sent = requests.post(self._locationOut, headers=headers,
                                     data=payload)
            except:
                print("Failure to send request")
        if typ == 'string':
            self.outString()
        if typ == 'csv':
            self.csvout()
            #create printer function that will create a csv output file.

    def htOut(self):
        payload_dict = {}
        payload_dict['mac'] = self._id
        payload_dict['speed_pitch_score'] = self._metrics._speed[0]
        payload_dict['speed_yaw_score'] = self._metrics._speed[1]
        payload_dict['speed_roll_score'] = self._metrics._speed[2]
        payload_dict['normalized_speed_pitch_score'] = self._metrics._speedNormal[0]
        payload_dict['normalized_speed_yaw_score'] = self._metrics._speedNormal[1]
        payload_dict['normalized_speed_roll_score'] = self._metrics._speedNormal[2]
        payload_dict['speed_score'] = self._metrics._speedScore
        payload_dict['strain_pitch_score'] = self._metrics._strain[0]
        payload_dict['strain_yaw_score'] = self._metrics._strain[1]
        payload_dict['strain_roll_score'] = self._metrics._strain[2]
        payload_dict['strain_score'] = self._metrics._strain[3]
        payload_dict['posture_pitch_score'] = self._metrics._posture[0]
        payload_dict['posture_yaw_score'] = self._metrics._posture[1]
        payload_dict['posture_roll_score'] = self._metrics._posture[2]
        payload_dict['posture_score'] = self._metrics._posture[3]
        payload_dict['safety_score'] = self._metrics._totalScore
        time = self._metrics._collection_structured_data_obj.time
        timeZero = time._index[0]
        timeEnd = time._index[-1]
        startTime = time[timeZero]
        endTime = time[timeEnd]
        payload_dict['start_time'] = startTime
        payload_dict['end_time'] = endTime
        analyzed = datetime.now().utcnow().isoformat()
        payload_dict['analyzed_at'] = analyzed
        return payload_dict

    def csvout(self):
        return

    def outString(self):
        return

