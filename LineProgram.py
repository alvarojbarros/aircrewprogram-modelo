import Tools

def fieldsDefinition():
    res = {}
    res['Aircraft'] = ('str',3)
    res['IdStart'] = ('int')
    res['StartDateTime'] = ('datetime')
    res['StartDate'] = ('date')
    res['StartTime'] = ('time')
    res['EndDateTime'] = ('datetime')
    res['EndDate'] = ('date')
    res['EndTime'] = ('time')
    return res

class LineProgram(object):

    def __init__(self,fields):
        if not Tools.validateFieldsType(fieldsDefinition(),fields): return
        self.initOk = True
        self.IdStart = int(fields.get('IdStart',0))
        self.Aircraft = fields.get('Aircraft',None)

        self.StartDateTime = Tools.stringToDateTime(fields.get('StartDateTime',None))
        self.StartDate = Tools.stringToDate(fields.get('StartDate',None))
        self.StartTime = Tools.stringToTime(fields.get('StartTime',None))

        self.EndDateTime = Tools.stringToDateTime(fields.get('EndDateTime',None))
        self.EndDate = Tools.stringToDate(fields.get('EndDate',None))
        self.EndTime = Tools.stringToTime(fields.get('EndTime',None))

        self.Elements = []

        if self.StartDateTime and not self.StartDate:
            self.StartDate = self.StartDateTime.date()
        if self.StartDateTime and not self.StartTime:
            self.StartTime = self.StartDateTime.time()
        if not self.StartDateTime and self.StartDate and self.Time:
            self.StartDateTime = datetime.combine(self.StartDate,self.Time)

        if self.EndDateTime and not self.EndDate:
            self.EndDate = self.EndDateTime.date()
        if self.EndDateTime and not self.EndTime:
            self.EndTime = self.EndDateTime.time()
        if not self.EndDateTime and self.EndDate and self.Time:
            self.EndDateTime = datetime.combine(self.EndDate,self.Time)


    def mandatoryFields(self):
        return ['Aircraft','StartDateTime','EndDateTime']

    def sortElements(self):
        self.Elements.sort(key=lambda x: x.StartDateTime )

    def checkAircraftElements(self):
        for e in self.Elements:
            if e.Aircraft != self.Aircraft:
                Tools.errorLog('Error en Aeronave %s %s %s' % (e.StartDate.strftime('%d/%m/%Y'),e.FlightNumber,e.Aircraft))
                return False
        return True

    def checkElementsOrder(self):
        l = len(self.Elements)
        for i in range(1,l):
            if self.Elements[i-1].StartDateTime >= self.Elements[i].StartDateTime:
                Tools.errorLog('Error en Orden %s %s %s' % (self.Elements[i].StartDateTime.strftime \
                    ('%Y%m%dT%H:%M:%S'),self.Elements[i].FlightNumber,self.Elements[i].Aircraft))
                return False
            elif self.Elements[i-1].StartDateTime > self.Elements[i].EndDateTime:
                Tools.errorLog('Error en Orden %s %s %s' % (self.Elements[i].StartDateTime.strftime \
                    ('%Y%m%dT%H:%M:%S'),self.Elements[i].FlightNumber,self.Elements[i].Aircraft))
                return False
            elif self.Elements[i-1].Destination != self.Elements[i].Origin:
                Tools.errorLog('Error en Origen/Destino %s %s %s' % (self.Elements[i].StartDateTime.strftime('%Y%m%dT%H:%M:%S') \
                    ,self.Elements[i].FlightNumber,self.Elements[i].Aircraft))
                return False
        return True

    def check(self):
        if not Tools.checkMandatoryFields(self): return False
        return True

    def checkElements(self):
        if not self.checkRepeats(): return False
        if not self.checkAircraftElements(): return False
        if not self.checkElementsOrder(): return False
        return True

    def checkRepeats(self):
        self.sortElements()
        from itertools import groupby
        for key, group in groupby(self.Elements):
            if len(list(group))>1:
                Tools.errorLog('Elemento Repetido %s %s' % (str(key)))
                return False
        return True
