import Tools
from Flight import Flight

class LineProgram(object):

    def fieldsDefinition(self):
        res = {}
        res['Aircraft'] = ('str',3)
        res['IdStart'] = ('int')
        res['StartDateTime'] = ('datetime')
        res['StartDate'] = ('date')
        res['StartTime'] = ('time')
        res['EndDateTime'] = ('datetime')
        res['EndDate'] = ('date')
        res['EndTime'] = ('time')
        res['Elements'] = ([])
        res['Flights'] = ({})
        res['Transfers'] = ([])
        res['Rest'] = ([])
        res['Others'] = ({})
        res['LocationDays'] = ({})
        res['DaysFree'] = ([])
        return res

    def __init__(self,fields={}):
        if not Tools.validateFieldsType(self.fieldsDefinition(),fields): return
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
        self.Flights = {}
        #los siguientes son atributos para el programa de una persona
        self.Transfers = []
        self.Others = {}
        self.Rest = []
        self.DaysFree = []
        self.LocationDays = {}

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

    def sortFlights(self):
        sorted(self.Flights.keys())

    def checkAircraft(self,listv):
        for e in listv:
            if e.Aircraft != self.Aircraft:
                Tools.errorLog('Error en Aeronave %s %s %s' % (e.StartDate.strftime('%d/%m/%Y'),e.FlightNumber,e.Aircraft))
                return False
        return True

    def checkElementsOrder(self,listv):
        l = len(listv)
        for i in range(1,l):
            if listv[i-1].StartDateTime >= listv[i].StartDateTime:
                #control de todos los elementos en orden sin superposicion
                Tools.errorLog('Error1 en Orden %s %s %s' % (listv[i].StartDateTime.strftime \
                    ('%Y%m%dT%H:%M:%S'),listv[i].FlightNumber,listv[i].Aircraft))
                return False
            #elif listv[i-1].StartDateTime > listv[i].EndDateTime:
            #    #control de todos los elementos en orden sin superposicion
            #    Tools.errorLog('Error2 en Orden %s %s %s' % (listv[i].StartDateTime.strftime \
            #        ('%Y%m%dT%H:%M:%S'),listv[i].FlightNumber,listv[i].Aircraft))
            #    return False
            elif listv[i-1].Destination != listv[i].Origin:
                #control de secuencialidad, Origen = Destino
                Tools.errorLog('Error en Origen/Destino %s %s %s %s %s %s' %  \
                    (listv[i-1].StartDateTime.strftime('%Y%m%dT%H:%M:%S') \
                    ,listv[i-1].FlightNumber,listv[i].Aircraft \
                    ,listv[i].StartDateTime.strftime('%Y%m%dT%H:%M:%S') \
                    ,listv[i].FlightNumber,listv[i].Aircraft))
                Tools.errorLog('Destino: %s, Origen: %s' % (listv[i-1].Destination,listv[i].Origin))
                return False
            #if listv[i-1].Type==1 and listv[i].Type==1:
            #    Tools.errorLog('Dos Vuelos Juntos %s %s %s' % (listv[i].StartDateTime.strftime \
            #        ('%Y%m%dT%H:%M:%S'),listv[i].FlightNumber,listv[i].Aircraft))
            #    return False
        return True

    def check(self):
        if not Tools.checkMandatoryFields(self): return False
        return True

    def checkElements(self):
        self.sortElements()
        if not self.checkRepeats(self.Elements): return False
        if not self.checkAircraft(self.Elements): return False
        if not self.checkElementsOrder(self.Elements): return False
        return True

    def checkRepeats(self,listv):
        from itertools import groupby
        for key, group in groupby(listv):
            if len(list(group))>1:
                Tools.errorLog('Elemento Repetido %s %s' % (str(key)))
                return False
        return True

    def checkFlights(self):
        self.sortFlights()
        if not self.checkRepeats(self.Flights): return False
        if not self.checkAircraft(self.Flights): return False
        if not self.checkElementsOrder(self.Flights): return False
        return True

    def addFligths(self,flights):
        for flight in flights:
            self.addFligth(flight,True)
        self.sortFlights()
        self.sortElements()

    def getNewKeyNumber(self):
        l = list(self.Flights)
        if l:
            return max(l) + 1
        else:
            return 1

    def addFligth(self,flight,AddSegment,key=None):
        if not key:
            key = self.getNewKeyNumber()
        #key = "%s-%s" %(flight.StartDateTime.strftime('%Y%m%d'),flight.FlightNumber)
        self.Flights[key] = flight
        if AddSegment:
            for segment in flight.Segments:
                self.Elements.append(segment)

    def findFlightByDateNumber(self,date,number):
        for key in self.Flights:
            flight = self.Flights[key]
            if flight.StartDate==date and flight.FlightNumber==number:
                return key

    def addElement(self,segment):
        self.Elements.append(segment)
        if segment.Type==1:
            #key = "%s-%s" %(segment.StartDateTime.strftime('%Y%m%d'),segment.FlightNumber)
            key = self.findFlightByDateNumber(segment.StartDate,segment.FlightNumber)
            if key:
                flight = self.Flights[key]
            else:
                key = self.getNewKeyNumber()
                flight = Flight()
            flight.addSegment(segment)
            self.addFligth(flight,False,key)

    def addPersonToFlight(self,person,flightNr):
        if flightNr in self.Flights:
            self.Flights[flightNr].addAircrew([person])

