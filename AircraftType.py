import Tools


class AircraftType(object):

    def fieldsDefinition(self):
        res = {}
        res['Code'] = ('str',10)
        res['Pax'] = ('int')
        res['CapacityKg'] = ('float')
        return res

    def __init__(self,fields):
        if not Tools.validateFieldsType(self.fieldsDefinition(),fields): return
        self.initOk = True
        self.Code = fields.get('Code',None)
        self.Pax = int(fields.get('Pax',0))
        self.CapacityKg = float(fields.get('CapacityKg',0))

    def mandatoryFields(self):
        return ['Code','Pax']

    def check(self):
        if not Tools.checkMandatoryFields(self): return False
        return True
