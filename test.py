import Tools
import json

if __name__ == "__main__":
    ''' aircrats = Tools.importJson('aircraft')
    aircrats = Tools.getObjectClass(aircrats,'Aircraft')
    segments = Tools.importJson('segment')
    segments = Tools.getObjectClass(segments,'Segment',['Origin','Destination'])
    aircrattypes = Tools.importJson('aircrafttype')
    aircrattypes = Tools.getObjectClass(aircrattypes,'AircraftType')
    airports = Tools.importJson('airport')
    airports = Tools.getObjectClass(airports,'Airport') '''
    movements = Tools.importJson('movements')
    movements = Tools.getObjectClass(movements,'AircraftMovement')
    lineprogram = Tools.importJson('lineprogram')
    lineprogram = Tools.getObjectClass(lineprogram,'LineProgram')
    lp = lineprogram[0]
    for e in movements:
        lp.addElement(e)
    print(lp.checkElements())
    f = open('vuelos.txt','w')
    jsonobj = json.dumps(lp.__dict__,default=Tools.json_serial,indent=4, separators=(',', ': '))
    f.write(jsonobj)
    f.close()

