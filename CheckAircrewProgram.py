from AircrewProgram import AircrewProgram
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
        key = "201610%s" % str(d).rjust(2,"0")
        date = datetime.strptime("%s-%s-%s" % (key[:4],key[4:6],key[6:]), "%Y-%m-%d").date()
        list = Person[d]
        k1 = 0
        origin = None
        for n in list:
            if k1==0 and isAirport(n,airports):
                origin = n
                k1 += 1
                continue
            #print("vuelo:",d,n,origin,k1,list)

            flight = None
            nkey = None
            segment = None
            if len(n)<3:
                #print(d,key,n)
                pass
            if len(n)>3:
                #print(n)
                if "/" in n:
                    pars = n.split("/")
                    k = 0
                    for nb in pars:
                        flight = None
                        nkey = None
                        segment = None
                        skip = False
                        if isAirport(nb,airports):
                            #print(origin,nb)
                            if k1>0:
                                segment = getSegmentByDestination(FlightPrograms,nb,date,origin)
                                if segment:
                                    origin = segment.Destination
                            else:
                                skip = True
                        elif len(nb)==3:
                            try:
                                n1 = int(nb)
                                nkey = key + "-" + nb
                            except:
                                pass
                        elif len(nb)==1 and k>0 and len(pars[0])==3:
                            fnumber = pars[0]
                            try:
                                n1 = int(fnumber)
                                nkey = key + "-" + fnumber[:2] + nb;
                            except:
                                pass
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
                        elif not skip:
                            if printF:
                                print(d,nb,"No Encontrado",list,k1,origin)
                            #print(d,n,list)
                            pass
                        k += 1

            elif len(n)==3:
                try:
                    n1 = int(n)
                    nkey = key + "-" + n
                except:
                    if isAirport(n,airports):
                        #if not flight:
                        #    flight = getFlightByDestination(FlightPrograms,n,date)
                        #print("buscando",n,date,origin)
                        segment = getSegmentByDestination(FlightPrograms,n,date,origin)
                        if segment:
                            #print (origin,segment.Origin,segment.Destination)
                            origin = segment.Destination
                    else:
                        if printF:
                            print(2,n,"No es vuelo",list,k1,origin)
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
                    pass
            k1 += 1

    return lp

def getAirportsDic(airports):
    res = {}
    for airport in airports:
        res[airport.Code] = airport
    return res

if __name__ == "__main__":

    ac = AircrewProgram()
    FlightPrograms = importFlightProgram()
    for aircraft in FlightPrograms:
        lp = FlightPrograms[aircraft]
        f = open('vuelos%s.txt' % aircraft,'w')
        jsonobj = json.dumps(lp.__dict__,default=Tools.json_serial,indent=4, separators=(',', ': '))
        f.write(jsonobj)
        f.close()

    Persons = importAircrewProgram()
    airports = Tools.importJson('datatest/airport.json')
    airports = Tools.getObjectClass(airports,'Airport')
    airports = getAirportsDic(airports)
    for person in sorted(Persons):
        print(person)
        pp = setPersonLineProgram(Persons[person],FlightPrograms,airports,False)
        if pp:
            acp = AircrewProgram()
            acp.checkLineProgram(None,person,pp)
        break
    #ac.checkLineProgram(programs,"BARROS")
