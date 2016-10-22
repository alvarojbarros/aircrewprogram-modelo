import Tools

class Airport(object):

    def fieldsDefinition(self):
        res = {}
        res['Code'] = ('str',3)
        res['Name'] = ('str',50)
        res['Country'] = ('str',2)
        res['Gap'] = ('time')
        return res

    def __init__(self,fields):
        if not Tools.validateFieldsType(self.fieldsDefinition(),fields): return
        self.initOk = True
        self.Code = fields.get('Code',None)
        self.Name = fields.get('Name',None)
        self.Country = fields.get('Country',None)
        self.Gap  = Tools.stringToTime(fields.get('Gap',None))

    def mandatoryFields(self):
        return ['Code','Gap']

    def check(self):
        if not Tools.checkMandatoryFields(self): return False
        return True
