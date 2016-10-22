from datetime import datetime
import Tools

class AircraftMovement(object):

    def fieldsDefinition(self):
        res = {}
        res['Origin'] = ('str',3)
        res['Destination'] = ('str',5)
        res['Aircraft'] = ('str',3)
        res['FlightType'] = ('int')
        res['Type'] = ('int')
        res['Editable'] = ('int')
        res['FlightNumber'] = ('str',3)
        res['Id'] = ('int')
        res['StartDateTime'] = ('datetime')
        res['StartDate'] = ('date')
        res['StartTime'] = ('time')
        res['EndDateTime'] = ('datetime')
        res['EndDate'] = ('date')
        res['EndTime'] = ('time')
        res['Time'] = ('time')
        res['Days'] = ('int')
        return res

    def __init__(self,fields):
        if not Tools.validateFieldsType(self.fieldsDefinition(),fields): return
        self.initOk = True
        self.Origin = fields.get('Origin',None)
        self.Destination = fields.get('Destination',None)
        self.Aircraft = fields.get('Aircraft',None)
        self.Type = int(fields.get('Type',0))
        self.FlightType = int(fields.get('Type',0))

        self.Editable = int(fields.get('Editable',1))
        self.FlightNumber = fields.get('FlightNumber',None)
        self.Id = int(fields.get('Id',0))

        self.StartDateTime = Tools.stringToDateTime(fields.get('StartDateTime',None))
        self.StartDate = Tools.stringToDate(fields.get('StartDate',None))
        self.StartTime = Tools.stringToTime(fields.get('StartTime',None))

        self.Time = Tools.stringToTime(fields.get('Time',None))
        self.Days = int(fields.get('Days',0))

        self.EndDateTime = Tools.stringToDateTime(fields.get('EndDateTime',None))
        self.EndDate = Tools.stringToDate(fields.get('EndDate',None))
        self.EndTime = Tools.stringToTime(fields.get('EndTime',None))

        if self.StartDateTime and not self.StartDate:
            self.StartDate = self.StartDateTime.date()
        if self.StartDateTime and not self.StartTime:
            self.StartTime = self.StartDateTime.time()
        if not self.StartDateTime and self.StartDate and self.Time:
            self.StartDateTime = datetime.combine(self.StartDate,self.Time)

        if not self.EndDateTime and self.StartDateTime and self.Time:
            self.EndDateTime = Tools.addTimeDaysToDatetime(self.Days,self.Time,self.StartDateTime)
        if not self.EndDate and self.EndDateTime:
            self.EndDate = self.EndDateTime.date()
        if not self.EndTime and self.EndDateTime:
            self.EndTime = self.EndDateTime.time()


    def types(self):
        return {1:"Segmento",2:"Gap",3:"Mantenimiento"}

    def flightTypes(self):
        return {1:"Regular",2:"Charter",3:"Ferry",4:"Instruccion",5:"Inspeccion",6:"Prueba de Mantenimiento",7:"Vuelo Especial"}

    def check(self):
        if not self.checkType(): return False
        #if not self.checkTime(): return False
        if not Tools.checkMandatoryFields(self): return False
        return True

    def mandatoryFields(self):
        return ['Origin','Destination','Aircraft','StartDateTime','Type','Time']

    def checkType(self):
        if self.Type in (2,3):
            if self.Origin!=self.Destination:
                Tools.errorLog('Error de Origen/Destino en Movimiento %s %s ' % (self.StartDateTime.strftime('%Y%m%dT%H:%M:%S'),self.Aircraft))
                return False
        return True

    def checkTime(self,segmets):
        if self.StartDateTime >= self.EndDateTime:
            Tools.errorLog('Error de horarios en Movimiento %s %s' % (self.StartDateTime.strftime('%Y%m%dT%H:%M:%S'),self.Aircraft))
            return False
        if segents.has_key((self.Origin,self.Destination)):
            if segents[(self.Origin,self.Destination)].FlightTime!=self.Time:
                Tools.errorLog('Error de Duracion en Movimiento %s %s' % (self.StartDateTime.strftime('%Y%m%dT%H:%M:%S'),self.Aircraft))
                return False
        return True