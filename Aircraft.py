import Tools

class Aircraft(object):

    def fieldsDefinition(self):
        res = {}
        res['Code'] = ('str',3)
        res['Name'] = ('str',20)
        res['Type'] = ('str',10)
        return res

    def __init__(self,fields):
        if not Tools.validateFieldsType(self.fieldsDefinition(),fields): return
        self.initOk = True
        self.Code = fields.get('Code',None)
        self.Name = fields.get('Name',None)
        self.Type = fields.get('Type',None)

    def mandatoryFields(self):
        return ['Code','Type']

    def check(self):
        if not Tools.checkMandatoryFields(self): return False
        return True
