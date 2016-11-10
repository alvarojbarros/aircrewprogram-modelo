from AircrewProgram import AircrewProgram,TRF
from FlightProrgamImport import *
from AircrewProgramImport import *
from LineProgram import LineProgram
import Tools
from datetime import datetime
import json


def findFlightByNumber(FlightPrograms,FlightNumber):
    for aircraft in FlightPrograms:
        program = FlightPrograms[aircraft]
        if FlightNumber in program.Flights:
            return program.Flights[FlightNumber]

def isAirport(code,airports):
    if code in airports:
        return True

def getFlightByDestination(FlightPrograms,dest,day):
    for aircraft in FlightPrograms:
        program = FlightPrograms[aircraft]
        for FlightNumber in program.Flights:
            flight = program.Flights[FlightNumber]
            if flight.StartDate==day and flight.Destination==dest:
                return flight

def getSegmentByDestination(FlightPrograms,dest,day,origin=None):
    for aircraft in FlightPrograms:
        program = FlightPrograms[aircraft]
        for segment in program.Elements:
            if segment.Type==1 and segment.StartDate==day and segment.Destination==dest and (not origin or origin==segment.Origin):
                    return segment


def setPersonLineProgram(Person,FlightPrograms,airports,printF=None):
    lp = LineProgram()
    for d in Person:
        key = "201611%s" % str(d).rjust(2,"0")
        dvalue = datetime.strptime("%s-%s-%s" % (key[:4],key[4:6],key[6:]), "%Y-%m-%d")
        date = dvalue.date()
        list = Person[d] #lista de movimientos para esa persona ese dia
        k1 = 0
        for n in list:
            found = False
            origin = None
            flight = None
            nkey = None
            segment = None
            if n in ('L','V','A','S','SP','G','MEDIA G','C','INMAE'):
                lp.Others[date] = n
            if len(n)<3:
                found = True
                continue
            if "/" in n:
                #si los vuelos vienen cargados separados con /, los proceso cada uno individual
                if "/" in n:
                    pars = n.split("/")
                    k = 0
                    for nb in pars:
                        flight = None
                        nkey = None
                        segment = None
                        skip = False
                        if len(nb)==3:
                            #intento generar el indicie con el numero de vuelo para buscar el vuelo en en el Programa de Vuelos
                            try:
                                n1 = int(nb)
                                nkey = key + "-" + nb
                            except:
                                pass
                        elif len(nb)==1 and k>0 and len(pars[0])==3:
                            #en este caso, los vuelos vienen de la siguiente forma 660/1
                            #genero el indice componiendo el vuelo con el vuelo anterior reemplazando el ultimo digito
                            fnumber = pars[0]
                            try:
                                n1 = int(fnumber)
                                nkey = key + "-" + fnumber[:2] + nb;
                            except:
                                pass
                        if nkey:
                            #busco el vuelo
                            flight = findFlightByNumber(FlightPrograms,nkey)
                        if flight:
                            #agrego el vuelo al programa de vuelos de la persona
                            lp.addFligth(flight,True)
                            if printF:
                                print(d,n,"%s-%s"%(flight.Origin,flight.Destination),flight.FlightNumber,"OK",list,k1,origin)
                        k += 1
            elif n[0]=="T":
                vnr = n[1:]
                nkey = key + "-" + vnr
                flight = findFlightByNumber(FlightPrograms,nkey)
                if flight:
                    lp.Transfers.append(TRF(flight.StartDateTime,flight.EndDateTime,flight.Origin,flight.Destination))
                elif isAirport(vnr,airports):
                    lp.Transfers.append(TRF(dvalue,None,None,vnr))
                found = True
            else:
                nkey = key + "-" + n
                if nkey:
                    flight = findFlightByNumber(FlightPrograms,nkey)
                if flight:
                    lp.addFligth(flight,True)
                    if printF:
                        print(d,n,"%s-%s"%(flight.Origin,flight.Destination),flight.FlightNumber,"OK",list,k1,origin)
                elif segment:
                    lp.addElement(segment)
                    if printF:
                        print(d,n,"%s-%s"%(segment.Origin,segment.Destination),segment.FlightNumber,"OK",list,k1,origin)
                else:
                    if printF:
                        print(d,n,"No Encontrado",list,k1,origin)
            k1 += 1

    return lp

def getAirportsDic(airports):
    res = {}
    for airport in airports:
        res[airport.Code] = airport
    return res

if __name__ == "__main__":

    ac = AircrewProgram()
    FlightPrograms = importFlightProgram('datatest/COMERCIAL NOVIEMBRE  VERSION TRES.csv')

    Persons = importAircrewProgram()
    airports = Tools.importJson('datatest/airport.json')
    airports = Tools.getObjectClass(airports,'Airport')
    airports = getAirportsDic(airports)
    PersonPrograms = {}
    for person in sorted(Persons):
        #if person=='WOLANOW':
        if True:
            pp = setPersonLineProgram(Persons[person],FlightPrograms,airports,False)
            if pp:
                for flightNr in pp.Flights:
                    for aircraft in FlightPrograms:
                        FlightPrograms[aircraft].addPersonToFlight(person,flightNr)
                PersonPrograms[person] = pp

    for aircraft in FlightPrograms:
        lp = FlightPrograms[aircraft]
        f = open('vuelos%s.txt' % aircraft,'w')
        jsonobj = json.dumps(lp.__dict__,default=Tools.json_serial,indent=4, separators=(',', ': '))
        f.write(jsonobj)
        f.close()

    test = 0
    if test == 0:
        for person in sorted(PersonPrograms):
            print(person)
            pp = PersonPrograms[person]
            acp = AircrewProgram()
            acp.checkLineProgram(None,person,pp)
    else:
        person = 'GIOSA'
        pp = PersonPrograms[person]
        acp = AircrewProgram()
        acp.checkLineProgram(None,person,pp)
