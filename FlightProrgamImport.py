import Tools
from AircraftMovement import AircraftMovement
from LineProgram import LineProgram
import json
import datetime

months = {'SEPTIEMBRE':9,'OCTUBRE':10,'NOVIEMBRE':11,'DICIEMBRE':12}
days = ['LUNES','MARTES','MIERCOLES','JUEVES','VIERNES','SABADO','DOMINGO']

def processAircraft(fields,aircraft):
    flights = []
    gaps = []
    found = False
    for value in fields:
        if value:
            found = True
    if not found:
        return flights,gaps

    vals = [None,None,None,None,None]
    gap = [None,None,None]
    k = 0
    for value in fields:
        if not value:
            vals = [None,None,None,None,None]
            gap = [None,None,None]
        if value:
            if not vals[0] and not gap[0]:
                vals[0] = value
                continue
            if vals[0] and not vals[1]:
                vals[1] = value
                continue
            if vals[0] and vals[1] and not vals[2]:
                vals[2] = value
                continue
            if vals[0] and vals[1] and vals[2] and not vals[3]:
                vals[3] = value
                continue
            if not vals[4] and vals[0] and vals[1] and vals[2] and vals[3]:
                vals[4] = value
                gap[0] = vals[3]
                gap[1] = vals[4]
                flights.append(vals)
                vals = [None,None,None,None,None]
                continue

            if gap[0] and not gap[1]:
                gap[1] = value
                continue
            if gap[0] and gap[1] and not gap[2] and value==gap[1]:
                if (k+1)<len(fields):
                    nextvalue = fields[k+1]
                    gap[2] = fields[k+1]
                    vals[0] = value
                    gaps.append(gap)
                gap = [None,None,None]
                continue

        k += 1
    if gaps and not gaps[len(gaps)-1][1]:
        gaps = gaps[:-1]
    return flights,gaps


def getMovementDics(fecha,aircarfts,gmovs):
    movs = []
    for key in sorted(aircarfts):
        d1 = datetime.datetime(fecha[0],fecha[1],fecha[2]).strftime("%Y-%m-%d")
        d2 = d1
        flights = aircarfts[key][0]
        gaps = aircarfts[key][1]
        if not flights and not gaps:
            continue
        if flights:
            for flight in flights:
                if flight[3]<flight[1]:
                    d2 = Tools.addDays(datetime.datetime(fecha[0],fecha[1],fecha[2]),1).strftime("%Y-%m-%d")
                #dic = [flight[0],flight[4],"%s %s:00" % (d1,flight[1]) ,"%s %s:00" % (d2,flight[3]),flight[2],1,key]
                dic = {"Origin":flight[0],"Destination":flight[4] \
                ,"StartDateTime": "%s %s:00" % (d1,flight[1]) \
                ,"EndDateTime": "%s %s:00" % (d2,flight[3]) \
                ,"FlightNumber": flight[2] \
                ,"Type": 1 \
                ,"Aircraft": key }

                movs.append(dic)
                #gmovs.append(dic)

        ''' if gaps:
            for gap in gaps:
                if gap[2]<gap[0]:
                    d1 = Tools.addDays(datetime.datetime(fecha[0],fecha[1],fecha[2]),1).strftime("%Y-%m-%d")
                dic = [gap[1],gap[1],"%s %s:00" % (d1,gap[0]),"%s %s:00" % (d2,gap[2]),'',2,key]

                # dic = {"Origin":gap[1],"Destination":gap[1] \,"StartDateTime": "%s %s:00" % (d1,gap[0]) \,"EndDateTime": "%s %s:00" % (d2,gap[2]) \,"Type": 2 \,"Aircraft": key \}
                movs.append(dic)
                gmovs.append(dic) '''
    #movs.sort()
    return movs


def importFlightProgram(f=None, filename=None):

    if not f:
        if not filename:
            return
        f = open(filename,'r')

    st = None
    et = None
    airlist = []

    newmovs = []
    aircarfts = {}
    fecha = [2016,None,None]
    process = False
    lastdate = None
    gmovs = []
    lines = str(f.read()).split('\\r\\n')
    for l in lines:
        fields = l.replace('\n','').split(';')
        if len(fields)<2:
            continue
        if fields[0]:

            if not fecha[2] and fields[0][0].isdigit():
                fecha[2] = int(fields[0])
            elif fecha[2] and not fields[0][0].isdigit():
                fecha[1] = int(months[fields[0]])
                lastdate = fecha
                fecha = [2016,None,None]

            if fields[0] in days and lastdate:

                movs = getMovementDics(lastdate,aircarfts,gmovs)
                for m in movs:
                    newmov = AircraftMovement(m)
                    newmovs.append(newmov)
                aircarfts = {}

        if len(fields[1])==3:
            if all(word[0].isupper() for word in fields[1]):

                flights,gaps = processAircraft(fields[2:],fields[1])
                aircarfts[fields[1]] = (flights,gaps)
                if fields[1] not in airlist:
                    airlist.append(fields[1])
    LinePrograms = {}
    for airc in airlist:
        lp = LineProgram({"Aircraft":airc,"StatDateTime":st,"EndDateTime":et})
        for e in newmovs:
            if e.Aircraft == airc:
                lp.addElement(e)
        LinePrograms[airc] = lp
    return LinePrograms
