import datetime
import Tools

def fieldsDefinition():
    res = {}
    res['Origin'] = ('str',3)
    res['Destination'] = ('str',3)
    res['FlightTime'] = ('time')
    res['Distance'] = ('float')
    res['BlockTime'] = ('time')
    return res

class Segment(object):


    def __init__(self,fields):
        if not Tools.validateFieldsType(fieldsDefinition(),fields): return
        self.initOk = True
        self.Origin = fields.get('Origin',None)
        self.Destination = fields.get('Destination',None)
        self.Distance = float(fields.get('Distance',0))
        self.FlightTime = Tools.stringToTime(fields.get('FlightTime',None))
        self.BockTime = Tools.stringToTime(fields.get('BockTime',None))

    def mandatoryFields(self):
        return ['Origin','Destination','FlightTime']

    def check(self):
        if not Tools.checkMandatoryFields(self): return False
        return True
