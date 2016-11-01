#encoding: utf-8

import Tools
from datetime import datetime,timedelta

#################
#
#  Definiciones
#   - TV: Tiempo de Vuelo
#   - TSV: Tiempo de Servicio de Vuelo
#
#  Ariculos de ley a cumplir
#
#  Articulos 3, 4, 5, 6, 7 y 9
#   3.1 - Tiempo de Vuelo
#   3.2 - Tiempo de Servicio de Vuelo
#
#  Articulo 8 - Tiempo Maximo de Vuelo Nocturno en un lapso de tiempo (14hs en 72hs)
#
#  Articulo 11 - Cantidad de Aterrizajes
#
#  Articulo 13 - 2 Pilotos en Tripulaciones de 3
#
#  Articulo 15 - Maxima cantidad de dias fuera de base (18 de 30)
#
#  Articulos 21, 23 y 24 - Tiempos de Descanso mínimos despues de TSV
#
#  Articulo 26 - Horas de Descanso consecutivas en 7 días corridos
#
#  Artículo 27 - Días de Descanso por mes calendario
#
#  Artículo 28 - Dias de Vacaciones
#
#  Artículo 25 - Despues de un cierto tiempo fuera de Base, el descanso correspondiente tiene que ser un 30% del tiempo fuera de base
#
#  Artiuclo 44 - El tiempo maximo entre TSV programado tiene que ser 3 horas
#
#  Dudas
#  1. Como se aplica el articulo 14. No se aplica
#  2. Como se aplica el articulo 25. El descanso correspondiente se considera en el 30%
#  3. Como se aplica el articulo 44. Maximo de 3 horas para que no se venza la programación entre TSV
#  4. Los dias fuera de base, se computan por pernocte fuera de base?
#
#
#  Configuraciones
#
#      "Base": ["AEP","EZE"], Bases
#      "NightTimeStart": "23:00:00", Inicio de Horario Nocturno
#      "NightTimeEnd": "06:00:00", Finalizacion de Horario Nocturno
#      "ServiceTimeAfterFlight": 30, TSV despues de Finalizar el vuelo
#      "ServiceTimeBeforeFlight": 60, TSV andes de Empezar el vuelo
#      "NightMaxTV": [72,14], Maximo TV en un lapso de tiempo: 14hs en 72hs
#      "NightTVSDisc": [60,30],
#      "MaxLandings24Hs": 6, Maxima cantidad de Aterizajes en 24 hs
#      "MaxHoursOutBase": 48,
#      "MaxDaysOutBase": 18, Maxima Cantidad de dias fuera de Base en 30 dias Calendario
#      "RestaTimeStart": 45, Tiempo entre finalizacion de TSV y el inicio Descanso (en minutos)
#      "NightRestLimit": 0.5, Limite de TSV a TSV nocturno
#      "NightRestAdditional": 120, Tiemp de Descanso adicional por TVS nocturno
#      "AddRestOutBase": 0.3, Articulo 25
#      "Art25": 4, Articulo 25
#      "WeekRestHours": 36, Horas consecutivas de descanso en un período de 7 días consecutivos
#      "TotalRest30": 10, Dias de descanso para meses de 30 o menos dias
#      "TotalRest31": 11, Dias de descanso para meses de 31 dias
#      "RestDaysInBase": 8, Días de descanso en base
#      "ContinuedLocalRest": 3, Dias de descanso continuados para vuelos cabotaje o limitrofes
#      "ContinuedInterRest": 4, Dias de descanso continuados para vuelos internacionales no limitrofes
#      "MaxHoursTS": 4, Maximo de horas entre vuelos para que no se consideren TSV diferentes
#      "GRest": 0.5,
#      "NightFraction": 1,
#      "HoursAddAuxiliar": 10,
#      "NightAddTime1": 15, Cantidad de Minutos que se restan al TSV por cada hora de TSV nocturno (en minutos) (con medios de descanso)
#      "NightAddTime2": 30, Cantidad de Minutos que se restan al TSV por cada hora de TSV nocturno (en minutos) (sin medios de descanso)
#
#
#################


class TSV(object): #Tiempo de Servicio de Vuelo

    def __init__(self):
        self.StartDateTime = None
        self.EndDateTime = None
        self.Time = None
        self.Segments = []

    def appendSegment(self,segment):
        self.Segments.append(segment)
        self.Segments.sort(key=lambda x: x.StartDateTime)
        self.StartDateTime = Tools.addMinutesToDateTime(self.Segments[0].StartDateTime,-settings['ServiceTimeBeforeFlight'])
        self.EndDateTime = Tools.addMinutesToDateTime(self.Segments[len(self.Segments)-1].EndDateTime,settings['ServiceTimeAfterFlight'])
        self.Time = self.EndDateTime - self.StartDateTime
        self.TimeHours = self.Time.seconds/3600

def getFlightsListFromSegments(Segments):
    res = []
    for s in Segments:
        if s.FlightNumber not in res:
            res.append(s.FlightNumber)
    return res

def getDestinationListFromSegments(Segments):
    res = []
    k = 0
    for s in Segments:
        if k==0:
            res.append(s.Origin)
        res.append(s.Destination)
        k += 1
    return res

def appendToNightSegments(s,StartTime=None,EndTime=None):
    #print(StartTime,EndTime)
    if s.StartDateTime not in NightSegments:
        tvn = TSV()
        st = s.StartDateTime
        et = s.EndDateTime
        tvn.StartDateTime = s.StartDateTime
        tvn.EndDateTime = s.EndDateTime
        if StartTime:
            tvn.StartDateTime = datetime(st.year,st.month,st.day,StartTime.hour,StartTime.minute)
        elif EndTime:
            tvn.EndDateTime = datetime(et.year,et.month,et.day,EndTime.hour,EndTime.minute)
        NightSegments[s.StartDateTime] = tvn

def checkQuantLandings(List,StartDateTime,EndDateTime,limit):
    #sumo cantidad de movimientos (para aterrizajes)
    t = 0
    for segment in List:
        if segment.EndDateTime>=StartDateTime and segment.EndDateTime<=EndDateTime and segment.StartDateTime<StartDateTime:
            t += 1
    if t>limit:
        return False
    return True


def checkTimes(List,StartDateTime,EndDateTime,limit,CheckNight=False):
    #sumo los tiempos en el periodo a controlar
    nlimit = limit
    t = 0
    SubMinutes = 0
    for segment in List:
        if segment.StartDateTime>=StartDateTime and segment.StartDateTime<=EndDateTime \
            and segment.EndDateTime<=EndDateTime:
            #todo el segmento dentro del perido a controlar
            td = segment.EndDateTime - segment.StartDateTime
            t += td.seconds / 60
        if segment.StartDateTime>=StartDateTime and segment.StartDateTime<=EndDateTime \
            and segment.EndDateTime>EndDateTime:
            #el segmento empieza en el periodo a controlar pero termina fuera
            td = EndDateTime - segment.StartDateTime
            t += td.seconds / 60
        if segment.EndDateTime>=StartDateTime and segment.EndDateTime<=EndDateTime \
            and segment.StartDateTime<StartDateTime:
            #el segmento empieza termina en el periodo a controlar pero empieza antes
            td = segment.EndDateTime - StartDateTime
            t += td.seconds / 60
        if CheckNight:
            diff = None
            if segment.StartDateTime.time()>=NightTimeStart and segment.EndDateTime.time()>=NightTimeStart:
                #4. empieza despues de las 23 y termina antes de las 24
                dif = Tools.timeDiff(segment.StartDateTime.time(),segment.EndDateTime.time())
                appendToNightSegments(segment)
            elif segment.StartDateTime.time()<=NightTimeEnd and segment.EndDateTime.time()<=NightTimeEnd:
                #7. empieza antes de las 6 y termina antes de las 6
                dif = Tools.timeDiff(segment.StartDateTime.time(),segment.EndDateTime.time())
                appendToNightSegments(segment)
            elif segment.StartDateTime.time()<=NightTimeEnd and segment.EndDateTime.time()>=NightTimeEnd:
                #8. empieza antes de las 6 y termina despues de las 6
                dif = Tools.timeDiff(segment.StartDateTime.time(),NightTimeEnd)
                appendToNightSegments(segment,EndTime=NightTimeEnd)
            elif segment.StartDateTime.time()<=NightTimeStart and segment.EndDateTime.time()>=NightTimeStart:
                #1. empieza antes de las 23 y termina despues de las 23
                dif = Tools.timeDiff(NightTimeStart,segment.EndDateTime.time())
                appendToNightSegments(segment,StartTime=NightTimeStart)
            elif segment.StartDateTime.time()<=NightTimeStart and segment.EndDateTime.time()<=NightTimeEnd \
                and segment.EndDateTime.time() <  segment.StartDateTime.time():
                #2. empieza antes de las 23 y termina antes de las 6
                dif = Tools.timeDiff(NightTimeStart,segment.EndDateTime.time())
                appendToNightSegments(segment,StartTime=NightTimeStart)
            elif segment.StartDateTime.time()<=NightTimeStart and segment.EndDateTime.time()>=NightTimeEnd \
                and segment.EndDateTime.time() <  segment.StartDateTime.time():
                #3. empieza antes de las 23 y termina despues de las 6
                dif = Tools.timeDiff(NightTimeStart,NightTimeEnd)
                appendToNightSegments(segment,StartTime=NightTimeStart,EndTime=NightTimeEnd)
            elif segment.StartDateTime.time()>=NightTimeStart and segment.EndDateTime.time()<=NightTimeEnd \
                and segment.EndDateTime.time() <  segment.StartDateTime.time():
                #5. empieza despues de las 23 y termina antes de las 6
                dif = Tools.timeDiff(segment.StartDateTime.time(),segment.EndDateTime.time())
                appendToNightSegments(segment)
            elif segment.StartDateTime.time()>=NightTimeStart and segment.EndDateTime.time()>=NightTimeEnd \
                and segment.EndDateTime.time() <  segment.StartDateTime.time():
                #6. empieza despues de las 23 y termina despues de las 6
                dif = Tools.timeDiff(segment.StartDateTime.time(),NightTimeEnd)
                appendToNightSegments(segment,EndTime=NightTimeEnd)
            if diff:
                print(segment.StartDateTime.time(),segment.EndDateTime.time())
                hours = int(dif.seconds/3600 + 1)
                SubMinutes += settings['NightAddTime2'] * hours

    nlimit += -SubMinutes
    if t>nlimit:
        return False
    return True

def checkSegment(List,segment,d,limit,CheckNight=False):
    StartTime = segment.StartDateTime
    EndTime = Tools.addTimeDaysToDatetime(d,0,segment.StartDateTime)
    res = checkTimes(List,StartTime,EndTime,limit,CheckNight)
    if not res: return False
    StartTime = Tools.addTimeDaysToDatetime(-d,0,segment.EndDateTime)
    EndTime = segment.StartDateTime
    res = checkTimes(List,StartTime,EndTime,limit,CheckNight)
    if not res: return False
    return True

def checkSegmentLandings(List,segment,d,limit):
    StartTime = segment.StartDateTime
    EndTime = Tools.addTimeDaysToDatetime(d,0,segment.StartDateTime)
    res = checkQuantLandings(List,StartTime,EndTime,limit)
    if not res: return False
    StartTime = Tools.addTimeDaysToDatetime(-d,0,segment.EndDateTime)
    EndTime = segment.StartDateTime
    res = checkQuantLandings(List,StartTime,EndTime,limit)
    if not res: return False
    return True

def appendError(error):
    if error not in Errors:
        Errors.append(error)

def checkNightTV(Segments):
    res = True
    for segment in Segments:
        if not checkSegment(Segments,segment,NightMaxTV[0]/24,NightMaxTV[1]):
            appendError("No cumple TV Nocurno %s hs en dia %s" % (NightMaxTV[1],segment.StartDateTime.strftime("%d/%m/%Y")))
            res = False
    return res

def checkLandings(Segments):
    res = True
    for segment in Segments:
        if not checkSegmentLandings(Segments,segment,1,MaxLandings24Hs):
            appendError("No cumple Cantidad de Aterrizajes en 24 hs %s hs en dia %s" % segment.StartDateTime.strftime("%d/%m/%Y"))
            res = False
    return res


def checkTV(Segments):
    res = True
    for segment in Segments:
        if not checkSegment(Segments,segment,1,tv24):
            appendError("No cumple TV 24 hs en dia %s" % segment.StartDateTime.strftime("%d/%m/%Y"))
            res = False
        if not checkSegment(Segments,segment,2,tv48):
            appendError("No cumple TV 48 hs en dia %s" % segment.StartDateTime.strftime("%d/%m/%Y"))
            res = False
        if not checkSegment(Segments,segment,7,tvWeek):
            appendError("No cumple TV 7 dias en dia %s" % segment.StartDateTime.strftime("%d/%m/%Y"))
            res = False

    Month = TSV()
    if len(Segments):
        Month.StartDateTime = Tools.firstDayOfMonth(Segments[0].StartDateTime)
        Month.EndDateTime = Tools.addMinutesToDateTime(Tools.addMonthToDateTime(1,Month.StartDateTime),-1)
        if not checkTimes(Segments,Month.StartDateTime,Month.EndDateTime,tvMonth):
            appendError("No cumple TV 30 dias en dia %s" % segment.StartDateTime.strftime("%d/%m/%Y"))
            res = False

        Month.StartDateTime = Tools.addMonthToDateTime(-1,Tools.firstDayOfMonth(Segments[0].StartDateTime))
        Month.EndDateTime = Tools.addMinutesToDateTime(Tools.addMonthToDateTime(1,Month.StartDateTime),-1)
        if not checkTimes(Segments,Month.StartDateTime,Month.EndDateTime,tvMonth):
            appendError("No cumple TV 30 dias en dia %s" % segment.StartDateTime.strftime("%d/%m/%Y"))
            res = False

    return res

def checkTSV(TSVlist):
    res = True
    for tsv in TSVlist:
        if not checkSegment(TSVlist,tsv,1,tsv24,True):
            appendError("No cumple TSV 24 hs en dia %s" % tsv.StartDateTime.strftime("%d/%m/%Y"))
            res = False
        if not checkSegment(TSVlist,tsv,2,tsv48):
            appendError("No cumple TSV 48 hs en dia %s" % tsv.StartDateTime.strftime("%d/%m/%Y"))
            res = False
        if not checkSegment(TSVlist,tsv,7,tsvWeek):
            appendError("No cumple TSV 7 dias en dia %s" % tsv.StartDateTime.strftime("%d/%m/%Y"))
            res = False

    Month = TSV()
    if len(TSVlist):
        Month.StartDateTime = Tools.firstDayOfMonth(TSVlist[0].StartDateTime)
        Month.EndDateTime = Tools.addMinutesToDateTime(Tools.addMonthToDateTime(1,Month.StartDateTime),-1)
        if not checkTimes(TSVlist,Month.StartDateTime,Month.EndDateTime,tvMonth):
            appendError("No cumple TV 30 dias en dia %s" % Month.StartDateTime.strftime("%d/%m/%Y"))
            res = False

        Month.StartDateTime = Tools.addMonthToDateTime(-1,Tools.firstDayOfMonth(TSVlist[0].StartDateTime))
        Month.EndDateTime = Tools.addMinutesToDateTime(Tools.addMonthToDateTime(1,Month.StartDateTime),-1)
        if not checkTimes(TSVlist,Month.StartDateTime,Month.EndDateTime,tvMonth):
            appendError("No cumple TV 30 dias en dia %s" % Month.StartDateTime.strftime("%d/%m/%Y"))
            res = False

    return res

class AircrewProgram(object):

    def checkLineProgram(self,LineProgram,person,PersonProgram=None):

        global settings
        settings = Tools.importJson('settings/config.txt')
        global NightTimeEnd
        NightTimeEnd = datetime.strptime(settings['NightTimeEnd'], "%H:%M:%S").time()
        global NightTimeStart
        NightTimeStart = datetime.strptime(settings['NightTimeStart'], "%H:%M:%S").time()

        tvlimits = Tools.importTable('settings/tvlimit.2.txt')
        global tsv24
        tsv24 = tvlimits[(2,0)]['TSV24Hr']*60
        global tv24
        tv24 = tvlimits[(2,0)]['TV24Hr']*60
        global tsv48
        tsv48 = tvlimits[(2,0)]['TSV48Hr']*60
        global tv48
        tv48 = tvlimits[(2,0)]['TV48Hr']*60
        global tsvWeek
        tsvWeek = tvlimits[(2,0)]['TSVWeek']*60
        global tvWeek
        tvWeek = tvlimits[(2,0)]['TVWeek']*60
        global tsvMonth
        tsvMonth = tvlimits[(2,0)]['TSVMonth']*60
        global tvMonth
        tvMonth = tvlimits[(2,0)]['TVMonth']*60
        global NightMaxTV
        NightMaxTV = settings['NightMaxTV']
        global MaxLandings24Hs
        MaxLandings24Hs = settings['MaxLandings24Hs']

        global Errors
        Errors = []
        global NightSegments
        NightSegments = {}



        PersonFlights = []
        if not PersonProgram:
            for key in LineProgram.Flights:
                flight = LineProgram.Flights[key]
                if person in flight.Aircrew:
                    PersonFlights.append(flight)
        else:
            for key in PersonProgram.Flights:
                flight = PersonProgram.Flights[key]
                if flight:
                    PersonFlights.append(flight)
        PersonFlights.sort(key=lambda x: x.StartDateTime)

        PersonSegments = []
        for f in PersonFlights:
            segments = f.Segments
            for segment in segments:
                if segment.Type==1:
                    PersonSegments.append(segment)
        PersonSegments.sort(key=lambda x: x.StartDateTime)

        #for s in PersonSegments:
        #    print (s.StartDateTime,s.FlightNumber,s.Origin,s.Destination)

        TSVlist = [] #lista con todos los tiempos de servicio de vuelo
        k = 0
        for s in PersonSegments:
            if k>0:
                sk = PersonSegments[k-1]
                td = s.StartDateTime - sk.EndDateTime
                if (td.seconds/3600 + td.days*24) > settings['MaxHoursTS']:
                    TSVlist.append(tsv)
                    tsv = TSV()
                else:
                    pass
                tsv.appendSegment(s)
            else:
                tsv = TSV()
                tsv.appendSegment(s)
            k += 1

        for tsv in TSVlist:
            #flights = getFlightsListFromSegments(tsv.Segments)
            #destlist = getDestinationListFromSegments(tsv.Segments)
            #print(flights,destlist)
            #print(tsv.StartDateTime,tsv.EndDateTime,tsv.Time)
            pass

        #Articulos 3, 4, 5, 6, 7 y 9
        res = True
        if not checkTV(PersonSegments):
            res = False
        if not checkTSV(TSVlist):
            res = False
        if not checkNightTV(PersonSegments):
            res = False
        if not checkLandings(PersonSegments):
            res = False

        if not res:
            print(person,Errors)
            print("")


##################
# Pendientes
# Algunos controles solo tienen que ser para el primer mes, no se tienen que hacer para el registro de vuelo