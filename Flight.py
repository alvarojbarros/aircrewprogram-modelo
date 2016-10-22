from datetime import datetime,timedelta
import Tools
from AircraftMovement import AircraftMovement

class Flight(object):

    def fieldsDefinition(self):
        res = {}
        res['Origin'] = ('str',3)
        res['Destination'] = ('str',5)
        res['Aircraft'] = ('str',3)
        res['FlightType'] = ('int')
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
        res['Segments'] = ([])
        return res

    def __init__(self,fields={}):
        if not Tools.validateFieldsType(self.fieldsDefinition(),fields): return
        self.initOk = True
        self.Origin = fields.get('Origin',None)
        self.Destination = fields.get('Destination',None)
        self.Aircraft = fields.get('Aircraft',None)
        self.FlightType = int(fields.get('FlightType',1))

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

        self.Segments = []

        self.getDateTimeFields()

    def getDateTimeFields(self):
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

    def flightTypes(self):
        return {1:"Regular",2:"Charter",3:"Ferry",4:"Instruccion",5:"Inspeccion",6:"Prueba de Mantenimiento",7:"Vuelo Especial"}

    def check(self):
        if not Tools.checkMandatoryFields(self): return False
        return True

    def mandatoryFields(self):
        return ['Origin','Destination','Aircraft','StartDateTime','Type','Time']

    def addSegment(self,movement):
        if movement.__class__.__name__!='AircraftMovement':
            Tools.errorLog('Error de Clase al Ingresar Movimiento %s %s ' % (self.StartDateTime.strftime('%Y%m%dT%H:%M:%S'),self.FlightNumber))
            return False
        if self.Aircraft and movement.Aircraft!=self.Aircraft:
            Tools.errorLog('Error al Ingresar Movimiento %s %s, No coincide Aeronave' % (self.StartDateTime.strftime('%Y%m%dT%H:%M:%S'),self.FlightNumber))
            return False
        elif not self.Aircraft:
            self.Aircraft = movement.Aircraft
        if self.FlightNumber and movement.FlightNumber!=self.FlightNumber:
            Tools.errorLog('Error al Ingresar Movimiento %s %s, No coincide Nr de Vuelo' % (self.StartDateTime.strftime('%Y%m%dT%H:%M:%S'),self.FlightNumber))
            return False
        elif not self.FlightNumber:
            self.FlightNumber = movement.FlightNumber
        if self.FlightNumber and movement.FlightNumber!=self.FlightNumber:
            Tools.errorLog('Error al Ingresar Movimiento %s %s, No coincide Nr de Vuelo' % (self.StartDateTime.strftime('%Y%m%dT%H:%M:%S'),self.FlightNumber))
            return False
        elif not self.FlightNumber:
            self.FlightNumber = movement.FlightNumber
        if self.FlightType and movement.FlightType!=self.FlightType:
            Tools.errorLog('Error al Ingresar Movimiento %s %s, No coincide Nr de Vuelo' % (self.StartDateTime.strftime('%Y%m%dT%H:%M:%S'),self.FlightNumber))
            return False
        elif not self.FlightType:
            self.FlightType = movement.FlightType

        self.Segments.append(movement)
        self.Segments.sort(key=lambda x: x.StartDateTime)
        l = len(self.Segments) - 1
        self.StartDateTime = self.Segments[0].StartDateTime
        self.StartDate = self.Segments[0].StartDate
        self.StartTime = self.Segments[0].StartTime
        self.EndDateTime = self.Segments[l].EndDateTime
        self.EndDate = self.Segments[l].EndDate
        self.EndTime = self.Segments[l].EndTime
        self.Origin = self.Segments[0].Origin
        self.Destination = self.Segments[l].Destination
        if not movement.Editable:
            self.Editable = movement.Editable
        #print(movement.StartDateTime,movement.Aircraft,movement.EndDateTime,movement.Origin,movement.Destination)
        tdelta = self.EndDateTime - self.StartDateTime
        self.Days = tdelta.days
        self.Time = timedelta(tdelta.seconds)
        return True