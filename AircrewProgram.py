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
#      "MaxLandings24Hs": 6, Maxima cantidad de Aterizajes en 24 hs
#      "MaxHoursOutBase": 48,        ---------no se esta usando-------------
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
#      "GRest": 0.5,      ---------no se esta usando------------- esta harcode, descanso por tiempo de guardia
#      "NightFraction": 1, ---------no se esta usando-------------
#      "HoursAddAuxiliar": 10, ---------no se esta usando-------------
#      "NightAddTime1": 15, Cantidad de Minutos que se restan al TSV por cada hora de TSV nocturno (en minutos) (con medios de descanso)
#      "NightAddTime2": 30, Cantidad de Minutos que se restan al TSV por cada hora de TSV nocturno (en minutos) (sin medios de descanso)
#
#
#################

class TRF(object): #Transfer

    def __init__(self,StartDateTime,EndDateTime,Origin,Destination):
        self.StartDateTime = StartDateTime
        self.EndDateTime = EndDateTime
        self.Origin = Origin
        self.Destination = Destination

class TSV(object): #Tiempo de Servicio de Vuelo

    def __init__(self):
        self.StartDateTime = None
        self.EndDateTime = None
        self.Time = None
        self.Segments = []
        self.Origin = None
        self.Destination = None

    def appendSegment(self,segment):
        self.Segments.append(segment)
        self.Segments.sort(key=lambda x: x.StartDateTime)
        self.Origin = self.Segments[0].Origin
        self.Destination = self.Segments[len(self.Segments)-1].Destination
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
    if s.StartDateTime not in [x.StartDateTime for x in NightSegments]:
        tvn = TSV()
        st = s.StartDateTime
        et = s.EndDateTime
        tvn.StartDateTime = s.StartDateTime
        tvn.EndDateTime = s.EndDateTime
        if StartTime:
            tvn.StartDateTime = datetime(st.year,st.month,st.day,StartTime.hour,StartTime.minute)
        elif EndTime:
            tvn.EndDateTime = datetime(et.year,et.month,et.day,EndTime.hour,EndTime.minute)
        if tvn not in NightSegments:
            NightSegments.append(tvn)

def checkQuantLandings(List,StartDateTime,EndDateTime,limit):
    #sumo cantidad de movimientos (para aterrizajes)
    t = 0
    for segment in List:
        if segment.EndDateTime>=StartDateTime and segment.EndDateTime<=EndDateTime and segment.StartDateTime<StartDateTime:
            t += 1
    if t>limit:
        return False
    return True


def checkTimes(List,StartDateTime,EndDateTime,limit,CheckNight=False,AddToNightSegment=False):
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

        if CheckNight or AddToNightSegment:
            dif = None
            if segment.StartDateTime.time()>=NightTimeStart and segment.EndDateTime.time()>=NightTimeStart:
                #4. empieza despues de las 23 y termina antes de las 24
                dif = Tools.timeDiff(segment.StartDateTime.time(),segment.EndDateTime.time())
                if AddToNightSegment:
                    appendToNightSegments(segment)
            elif segment.StartDateTime.time()<=NightTimeEnd and segment.EndDateTime.time()<=NightTimeEnd:
                #7. empieza antes de las 6 y termina antes de las 6
                dif = Tools.timeDiff(segment.StartDateTime.time(),segment.EndDateTime.time())
                if AddToNightSegment:
                    appendToNightSegments(segment)
            elif segment.StartDateTime.time()<=NightTimeEnd and segment.EndDateTime.time()>=NightTimeEnd:
                #8. empieza antes de las 6 y termina despues de las 6
                dif = Tools.timeDiff(segment.StartDateTime.time(),NightTimeEnd)
                if AddToNightSegment:
                    appendToNightSegments(segment,EndTime=NightTimeEnd)
            elif segment.StartDateTime.time()<=NightTimeStart and segment.EndDateTime.time()>=NightTimeStart:
                #1. empieza antes de las 23 y termina despues de las 23
                dif = Tools.timeDiff(NightTimeStart,segment.EndDateTime.time())
                if AddToNightSegment:
                    appendToNightSegments(segment,StartTime=NightTimeStart)
            elif segment.StartDateTime.time()<=NightTimeStart and segment.EndDateTime.time()<=NightTimeEnd \
                and segment.EndDateTime.time() <  segment.StartDateTime.time():
                #2. empieza antes de las 23 y termina antes de las 6
                dif = Tools.timeDiff(NightTimeStart,segment.EndDateTime.time())
                if AddToNightSegment:
                    appendToNightSegments(segment,StartTime=NightTimeStart)
            elif segment.StartDateTime.time()<=NightTimeStart and segment.EndDateTime.time()>=NightTimeEnd \
                and segment.EndDateTime.time() <  segment.StartDateTime.time():
                #3. empieza antes de las 23 y termina despues de las 6
                dif = Tools.timeDiff(NightTimeStart,NightTimeEnd)
                if AddToNightSegment:
                    appendToNightSegments(segment,StartTime=NightTimeStart,EndTime=NightTimeEnd)
            elif segment.StartDateTime.time()>=NightTimeStart and segment.EndDateTime.time()<=NightTimeEnd \
                and segment.EndDateTime.time() <  segment.StartDateTime.time():
                #5. empieza despues de las 23 y termina antes de las 6
                dif = Tools.timeDiff(segment.StartDateTime.time(),segment.EndDateTime.time())
                if AddToNightSegment:
                    appendToNightSegments(segment)
            elif segment.StartDateTime.time()>=NightTimeStart and segment.EndDateTime.time()>=NightTimeEnd \
                and segment.EndDateTime.time() <  segment.StartDateTime.time():
                #6. empieza despues de las 23 y termina despues de las 6
                dif = Tools.timeDiff(segment.StartDateTime.time(),NightTimeEnd)
                if AddToNightSegment:
                    appendToNightSegments(segment,EndTime=NightTimeEnd)
            if dif:
                segment.NightTime = dif
                if CheckNight:
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
    if not res:
        return False
    StartTime = Tools.addTimeDaysToDatetime(-d,0,segment.EndDateTime)
    EndTime = segment.StartDateTime
    res = checkTimes(List,StartTime,EndTime,limit,CheckNight)
    if not res:
        return False
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
        if not checkSegment(Segments,segment,NightMaxTV[0]/24,NightMaxTV[1]*60):
            appendError("No cumple TV Nocturno %s hs en dia %s" % (NightMaxTV[1],segment.StartDateTime.strftime("%d/%m/%Y")))
            #return False
            res = False
    return res

def checkLandings(Segments):
    res = True
    for segment in Segments:
        if not checkSegmentLandings(Segments,segment,1,MaxLandings24Hs):
            appendError("No cumple Cantidad de Aterrizajes en 24 hs %s hs en dia %s" % segment.StartDateTime.strftime("%d/%m/%Y"))
            #return False
            res = False
    return res

def getTSVforSegment(segment,TSVlist):
    for tsv in TSVlist:
        if segment.StartDateTime >= tsv.StartDateTime and segment.EndDateTime <= tsv.StartDateTime:
            return tsv


def checkTV(Segments,TSVlist):
    res = True
    for segment in Segments:
        tsv = getTSVforSegment(segment,TSVlist)
        if tsv and tsv.Segments:
            if not checkSegment(tsv.Segments,segment,1,tv24):
                appendError("No cumple TV 24 hs en dia %s" % segment.StartDateTime.strftime("%d/%m/%Y"))
                #return False
                res = False
        if not checkSegment(Segments,segment,2,tv48):
            appendError("No cumple TV 48 hs en dia %s" % segment.StartDateTime.strftime("%d/%m/%Y"))
            #return False
            res = False
        if not checkSegment(Segments,segment,7,tvWeek):
            appendError("No cumple TV 7 dias en dia %s" % segment.StartDateTime.strftime("%d/%m/%Y"))
            #return False
            res = False

    Month = TSV()
    if len(Segments):
        Month.StartDateTime = Tools.firstDayOfMonth(Segments[0].StartDateTime)
        Month.EndDateTime = Tools.addMinutesToDateTime(Tools.addMonthToDateTime(1,Month.StartDateTime),-1)
        if not checkTimes(Segments,Month.StartDateTime,Month.EndDateTime,tvMonth,AddToNightSegment=True):
            appendError("No cumple TV 30 dias en dia %s" % segment.StartDateTime.strftime("%d/%m/%Y"))
            #return False
            res = False

        #Month.StartDateTime = Tools.addMonthToDateTime(-1,Tools.firstDayOfMonth(Segments[0].StartDateTime))
        #Month.EndDateTime = Tools.addMinutesToDateTime(Tools.addMonthToDateTime(1,Month.StartDateTime),-1)
        #if not checkTimes(Segments,Month.StartDateTime,Month.EndDateTime,tvMonth):
        #    appendError("No cumple TV 30 dias en dia %s" % segment.StartDateTime.strftime("%d/%m/%Y"))
        #    return False
        #    res = False

    return res

def checkTSV(TSVlist):
    res = True
    for tsv in TSVlist:
        #if not checkSegment(TSVlist,tsv,1,tsv24,True):
        if not checkSegment([tsv],tsv,1,tsv24,CheckNight=True):
            appendError("No cumple TSV 24 hs en dia %s" % tsv.StartDateTime.strftime("%d/%m/%Y"))
            #return False
            res = False
        if not checkSegment(TSVlist,tsv,2,tsv48):
            appendError("No cumple TSV 48 hs en dia %s" % tsv.StartDateTime.strftime("%d/%m/%Y"))
            #return False
            res = False
        if not checkSegment(TSVlist,tsv,7,tsvWeek):
            appendError("No cumple TSV 7 dias en dia %s" % tsv.StartDateTime.strftime("%d/%m/%Y"))
            #return False
            res = False

    Month = TSV()
    if len(TSVlist):
        Month.StartDateTime = Tools.firstDayOfMonth(TSVlist[0].StartDateTime)
        Month.EndDateTime = Tools.addMinutesToDateTime(Tools.addMonthToDateTime(1,Month.StartDateTime),-1)
        if not checkTimes(TSVlist,Month.StartDateTime,Month.EndDateTime,tvMonth):
            appendError("No cumple TV 30 dias en dia %s" % Month.StartDateTime.strftime("%d/%m/%Y"))
            #return False
            res = False

        #Month.StartDateTime = Tools.addMonthToDateTime(-1,Tools.firstDayOfMonth(TSVlist[0].StartDateTime))
        #Month.EndDateTime = Tools.addMinutesToDateTime(Tools.addMonthToDateTime(1,Month.StartDateTime),-1)
        #if not checkTimes(TSVlist,Month.StartDateTime,Month.EndDateTime,tvMonth):
        #    appendError("No cumple TV 30 dias en dia %s" % Month.StartDateTime.strftime("%d/%m/%Y"))
        #    return False
        #    res = False

    return res

def checkDaysOutOfBase(PersonProgram,PersonFlights):
    Transfers = PersonProgram.Transfers
    list1 = []
    for f in PersonFlights:
        #list.append((f.FlightNumber,f.StartDateTime,f.Origin,f.Destination))
        list1.append(f)
    for t in Transfers:
        #list.append((None,t.StartDateTime,t.Origin,t.Destination))
        list1.append(t)
    #list.sort(key=lambda x: x[1])
    list1.sort(key=lambda x: x.StartDateTime)
    if not list1:
        return True
    #MontDates = Tools.lastDayOfMonth(list[0][1]).day
    MontDates = Tools.lastDayOfMonth(list1[0].StartDateTime).day
    if not 1:
        return True

    days = {}

    if list1[0].Origin in Bases:
        for i in range(1,list1[0].StartDateTime.day):
            days[i] = list1[0].Origin
    for f in list1:
        days[f.StartDateTime.day] = f.Destination

    for i in range(1,MontDates+1):
        if i in days:
            dest = days[i]
        else:
            days[i] = dest
    cnt = 0

    PersonProgram.LocationDays = days

    for i in days:
        if days[i] not in Bases:
            cnt += 1

    MaxDaysOutBase = settings['MaxDaysOutBase']
    if cnt>MaxDaysOutBase:
        appendError("Mas de %i dias fuera de base: % i dias" % (MaxDaysOutBase,cnt))
        #return False

    return True

def getBeforeStart(k,MyList):
    for i in range(k-2,-1,-1):
        tup = MyList[i]
        if tup[1] == 0 and tup[2].Origin in Bases:
            return tup
        elif tup[1] == 2 and tup[2].Origin in Bases:
            return tup

def getNextStart(k,MyList):
    for i in range(k,len(MyList)):
        tup = MyList[i]
        if tup[2] not in ('L','V','D','S'):
            return tup

def checkRestTimes(TSVList,PersonProgram):

    MyList = []
    for tsv in TSVList:
        MyList.append((tsv.StartDateTime,0,tsv,tsv.EndDateTime))

    for trf in PersonProgram.Transfers:
        MyList.append((trf.StartDateTime,2,trf,trf.EndDateTime))

    MyList.sort(key=lambda x: x[0])

    lastDest = None
    for mov in MyList:
        if lastDest and mov[2].Origin!=lastDest and lastDest not in Bases:
            appendError("Secuencia de Vuelos Incorrecta")
            #return False
        lastDest = mov[2].Destination

    for d in sorted(PersonProgram.Others):
        if PersonProgram.Others[d] == 'C':
            mydate1 = datetime(d.year,d.month,d.day,9,0)
            mydate2 = datetime(d.year,d.month,d.day,18,0)
            MyList.append((mydate1,1,PersonProgram.Others[d],mydate2))
        elif PersonProgram.Others[d] == 'INMAE':
            mydate1 = datetime(d.year,d.month,d.day,7,0)
            mydate2 = datetime(d.year,d.month,d.day,11,0)
            MyList.append((mydate1,1,PersonProgram.Others[d],mydate2))
        elif PersonProgram.Others[d] == 'G':
            mydate1 = datetime(d.year,d.month,d.day,0,0)
            mydate2 = Tools.addDaysToDatetime(1,mydate1)
            MyList.append((mydate1,1,PersonProgram.Others[d],mydate2))
        elif PersonProgram.Others[d] == 'MEDIA G':
            mydate1 = datetime(d.year,d.month,d.day,0,0)
            mydate2 = Tools.addDaysToDatetime(1,mydate1)
            mydate1 = datetime(d.year,d.month,d.day,12,0)
            MyList.append((mydate1,1,PersonProgram.Others[d],mydate2))
        #elif PersonProgram.Others[d] not in ('L','D','V','A','S','SP'):
        #    mydate = datetime(d.year,d.month,d.day,0,0)
        #    MyList.append((mydate,1,PersonProgram.Others[d],Tools.addDaysToDatetime(1,mydate)))

    if not MyList:
        return True

    MyList.sort(key=lambda x: x[0])

    DaysFree = []
    k = Tools.lastDayOfMonth(MyList[0][0]).day
    for i in range(k):
        DaysFree.append(i+1)

    for tup in MyList:
        isTsv = not tup[1]
        Obj = tup[2]
        if isTsv or Obj in ('C','INMAE','G','MEDIA G'):
            DaysFree.remove(tup[0].day)

    for d in PersonProgram.Others:
        if PersonProgram.Others[d]=='S':
            DaysFree.remove(d.day)

    if k==31:
        TotalRestDays = settings['TotalRest31']
    else:
        TotalRestDays = settings['TotalRest30']
    if len(DaysFree) < TotalRestDays:
        appendError("No cumple Cantidad de dias Libres en el mes")
        #return False

    found = False
    c = 0
    ContinuedLocalRest = settings['ContinuedLocalRest']
    for i in range(len(DaysFree)):
        df = DaysFree[i]
        if i>0:
            if (df-1) == DaysFree[i-1]:
                c += 1
            else:
                c = 0
            if c>=ContinuedLocalRest-1:
                found = True
                break
    if not found:
        appendError("No cumple %i de dias Libres seguidos en el mes" % ContinuedLocalRest)
        #return False

    RestDaysInBase = settings['RestDaysInBase']
    c = 0
    for d in DaysFree:
        if PersonProgram.LocationDays[d] in Bases:
            c += 1
    if c<RestDaysInBase:
        appendError("No Cumple %i Dias de Descanso en Base" % RestDaysInBase)
        #return False

    AddRestOutBase = settings['AddRestOutBase']
    Art25 = settings['Art25']

    k = 0
    for tup in MyList:
        k += 1
        isTsv = not tup[1]
        Obj = tup[2]
        #if not isTsv and Obj in ('L','D','V','A','S'):
        #    #no es tsv, y es descanso o libre o vacaciones
        #    continue
        EndDateTime = tup[3]
        StartDateTime = tup[0]
        if k==1:
            RealRestStart = Tools.firstDayOfMonth(StartDateTime)
            #RealRestStart  = datetime(firstDay.year,firstDay.month,firstDay.day,0,0)
            RealRestEnd  = StartDateTime
            PersonProgram.Rest.append((RealRestStart,RealRestEnd))

        RestStart = EndDateTime
        if isTsv:
            RestStart = Tools.addMinutesToDateTime(EndDateTime,RestaTimeStart)
        ts = EndDateTime - StartDateTime
        tsh = ts.seconds/3600 + (ts.days * 24)
        RestEnd = None
        RealRestStart = RestStart
        RealRestEnd = None
        if Obj=='G':
            RestEnd = Tools.addHoursToDateTime(RestStart,12)
        elif Obj=='MEDIA G':
            RestEnd = Tools.addHoursToDateTime(RestStart,6)
        elif Obj == 'C':
            RestEnd = Tools.addHoursToDateTime(RestStart,8)
        elif Obj == 'INMAE':
            RestEnd = Tools.addHoursToDateTime(RestStart,2)
        elif tup[1] == 2:
            RestEnd = RestStart #verificar
        elif isTsv:
            for rest in RestSettings:
                if isTsv and tsh > rest['From'] and tsh <= rest['To']:
                    RestEnd = Tools.addHoursToDateTime(RestStart,rest['Rest'])
                    if hasattr(Obj,"NightTime"):
                        RestEnd = Tools.addHoursToDateTime(RestStart,rest['NightRest'])
                        if (EndDateTime - StartDateTime).seconds/3600 > NightRestLimit:
                            RestEnd = Tools.addMinutesToDateTime(RestEnd,NightRestAdditional)
                    break
            Origin = Obj.Origin
            #for s in Obj.Segments:
            #    Destination = Obj.Segments[len(Obj.Segments)-1].Destination
            if Obj.Origin not in Bases:
                beforeTsvInBase = getBeforeStart(k,MyList)
                if beforeTsvInBase:
                    DaysOut = StartDateTime.day - beforeTsvInBase[3].day - 1
                    if DaysOut > 0:
                        if DaysOut > Art25:
                            DaysOut = Art25
                        TimeAdd = DaysOut * 24 * AddRestOutBase * 60
                        NewRestEnd = Tools.addHoursToDateTime(RestStart,rest['Rest'])
                        NewRestEnd = Tools.addMinutesToDateTime(NewRestEnd,TimeAdd)
                        if NewRestEnd > RestEnd:
                            RestEnd = NewRestEnd
        if len(MyList)>k:
            nextTsv = getNextStart(k,MyList)
            skip = False
            if not isTsv and nextTsv[1] and nextTsv[2] in ('S','INMAE'):
                skip = True
            if not skip:
                NextStart = nextTsv[0]
                if NextStart<RestEnd:
                    appendError("No cumple Descanso despues de TS en dia %s" % RestStart.strftime("%d/%m/%Y"))
                    #return False
                RealRestEnd = NextStart
        else:
            firstDay = Tools.addDaysToDatetime(1,Tools.lastDayOfMonth(RealRestStart))
            RealRestEnd = datetime(firstDay.year,firstDay.month,firstDay.day,0,0)

        if RealRestStart and RealRestEnd:
            PersonProgram.Rest.append((RealRestStart,RealRestEnd))

    #for rest in PersonProgram.Rest:
    #    print(rest[0],rest[1])

    WeekRestHours = settings['WeekRestHours']

    d = Tools.firstDayOfMonth(MyList[0][0])
    d = datetime(2016,11,13)
    toDate = Tools.addDaysToDatetime(-7,Tools.lastDayOfMonth(MyList[0][0]))
    while d <= toDate:
        td = Tools.addDaysToDatetime(7,d)
        found = False
        DayFree = False
        for rest in PersonProgram.Rest:
            skip = False
            if rest[1]<d or rest[0]>td:
                skip = True
            if not skip:
                RestStart = None
                RestEnd = None
                if rest[0]>d:
                    RestStart = rest[0]
                else:
                    RestStart = d
                if rest[1]<td:
                    RestEnd = rest[1]
                else:
                    RestEnd = td
                dif = RestEnd - RestStart
                dif = (dif.days*24) + (dif.seconds/3600)
                if dif>WeekRestHours:
                    found = True
                    break
        if not found:
            appendError("No cumple Descanso de %i Horas entre %s y %s" % (WeekRestHours,d.strftime("%d/%m/%Y"),td.strftime("%d/%m/%Y")))
            #return False
        d = Tools.addDaysToDatetime(1,d)
    return True


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
        NightSegments = []
        global RestaTimeStart
        RestaTimeStart = settings['RestaTimeStart']
        global NightRestLimit
        NightRestLimit = settings['NightRestLimit']
        global NightRestAdditional
        NightRestAdditional = settings['NightRestAdditional']
        global RestSettings
        RestSettings = Tools.importRest('settings/rest.txt')
        global Bases
        Bases = settings['Base']



        tdif = Tools.timeDiff(NightTimeEnd,NightTimeStart)
        NightRestLimit = (24 - tdif.seconds/3600) * NightRestLimit


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
        tsv = None
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
        if tsv:
            TSVlist.append(tsv)
        #for tsv in TSVlist:
        #    flights = getFlightsListFromSegments(tsv.Segments)
        #    destlist = getDestinationListFromSegments(tsv.Segments)
        #    print(flights,destlist)
        #    print(tsv.StartDateTime,tsv.EndDateTime,tsv.Time)

        res = True



        #  Articulos 3, 4, 5, 6, 7 y 9
        if not checkTV(PersonSegments,TSVlist): res = False
        #  Articulos 3, 4, 5, 6, 7 y 9
        if not checkTSV(TSVlist): res = False
        # Articulo 8
        if not checkNightTV(NightSegments): res = False
        #  Articulo 11 - Cantidad de Aterrizajes
        if not checkLandings(PersonSegments): res = False
        #  Articulo 15 - Maxima cantidad de dias fuera de base (18 de 30)
        if not checkDaysOutOfBase(PersonProgram,PersonFlights): res = False
        #  Articulos 21, 23 y 24 - Tiempos de Descanso mínimos despues de TSV
        if not checkRestTimes(TSVlist,PersonProgram): res = False

        return Errors

        if not res:
            print(person,Errors)
            print("")

##################
# Pendientes
# Algunos controles solo tienen que ser para el primer mes, no se tienen que hacer para el registro de vuelo