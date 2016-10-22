import Tools
from AircraftMovement import AircraftMovement
from LineProgram import LineProgram

months = {'OCTUBRE':10,'NOVIEMBRE':11}

def processAircraft(fields):
    flights = []
    gaps = []
    vals = [None,None,None,None,None]
    gap = [None,None,None]
    for value in fields:
        if not value:
            vals = [None,None,None,None,None]
            gap = [None,None,None]
        if value:
            if gap[0] and not gap[1]:
                if not value[0].isdigit():
                    gap[1] = value
                else:
                    gap[2] = value
                    if gap[0] and gap[1] and gap[2]:
                        gaps.append(gap)
                    gap = [None,None,None]

            if not value[0].isdigit():
                if not vals[0]:
                    vals[0] = value
                elif not vals[4]:
                    vals[4] = value
                    gap[0] = vals[3]
                    if vals[0] and vals[1] and vals[2] and vals[3] and vals[4]:
                        flights.append(vals)
                    vals = [None,None,None,None,None]
            elif vals[0]:
                if not vals[1]:
                    vals[1] = value
                elif not vals[2]:
                    vals[2] = str(int(value[:3]))
                elif not vals[3]:
                    vals[3] = value

    if gaps and not gaps[len(gaps)-1][1]:
        gaps = gaps[:-1]
    return flights,gaps


def getMovementDics(fecha,aircarfts):
    movs = []
    d = "%s-%s-%s" %(fecha[0],str(fecha[1]).rjust(2,'0'),str(fecha[2]).rjust(2,'0'))
    for key in aircarfts:
        flights = aircarfts[key][0]
        gaps = aircarfts[key][1]
        for flight in flights:
            dic = {"Origin":flight[0],"Destination":flight[4] \
            ,"StartDateTime": "%s %s:00" % (d,flight[1]) \
            ,"EndDateTime": "%s %s:00" % (d,flight[3]) \
            ,"FlightNumber": flight[2] \
            ,"Type": 1 \
            ,"Aircraft": key \
            }
            movs.append(dic)

        for gap in gaps:
            dic = {"Origin":gap[1],"Destination":gap[1] \
            ,"StartDateTime": "%s %s:00" % (d,gap[0]) \
            ,"EndDateTime": "%s %s:00" % (d,gap[2]) \
            ,"Type": 2 \
            ,"Aircraft": key \
            }
            movs.append(dic)
    return movs

if __name__ == "__main__":

    f = open('Octubre VS 2.csv','r')

    st = None
    et = None
    airlist = []

    newmovs = []
    aircarfts = {}
    fecha = [2016,None,None]
    for l in f:
        fields = l.replace('TRASL','000').replace('trasl','000').split(';')
        if fields[0]:

            if not fecha[2] and fields[0][0].isdigit():
                fecha[2] = int(fields[0])
            elif fecha[2] and not fields[0][0].isdigit():
                fecha[1] = int(months[fields[0]])

                movs = getMovementDics(fecha,aircarfts)
                for m in movs:
                    newmov = AircraftMovement(m)
                    newmovs.append(newmov)
                aircarfts = {}
                if not st:
                    st = "%s-%s-%s 00:00:00" %(fecha[0],str(fecha[1]).rjust(2,'0'),str(fecha[2]).rjust(2,'0'))
                et = "%s-%s-%s 00:00:00" %(fecha[0],str(fecha[1]).rjust(2,'0'),str(fecha[2]).rjust(2,'0'))
                fecha = [2016,None,None]
        if len(fields[1])==3:
            if all(word[0].isupper() for word in fields[1]):
                flights,gaps = processAircraft(fields[2:])
                aircarfts[fields[1]] = (flights,gaps)
                if fields[1] not in airlist:
                    airlist.append(fields[1])
    for airc in airlist:
        lp = LineProgram({"Aircraft":airc,"StatDateTime":st,"EndDateTime":et})
        for e in newmovs:
            if e.Aircraft == airc:
                lp.addElement(e)
        print (airc,lp.checkElements())