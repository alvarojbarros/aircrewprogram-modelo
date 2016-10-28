#encoding: utf-8

import Tools

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
#
#  Dudas
#  1. Como se aplica el articulo 14
#  2. Como se aplica el articulo 25
#  3. Como se aplica el articulo 44
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
        #self.StartDateTime = self.Segments[0].StartDateTime
        #self.EndDateTime = self.Segments[len(self.Segments)-1].EndDateTime
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

class AircrewProgram(object):

    #TEV = 4 #tiempo entre vuelos para indicar que comienza otro TVS (tiempo de servicio de vuelo)

    def checkLineProgram(self,LineProgram,person,PersonProgram=None):

        global settings
        settings = Tools.importJson('settings/config.txt')

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
            print(tsv.StartDateTime,tsv.EndDateTime,tsv.Time)

