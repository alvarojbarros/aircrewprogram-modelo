import Tools
from AircraftMovement import AircraftMovement
from LineProgram import LineProgram
import json
import datetime

days = ['LUNES','MARTES','MIERCOLES','JUEVES','VIERNES','SABADO','DOMINGO']

def importAircrewProgram(f=None,filename=None):

    if not f:
        if not filename:
            return
        f = open(filename,'r')

    f1 = False
    persons = {}
    currentName = None
    k = 0
    lmonth = None
    lines = str(f.read()).split('\\r\\n')
    for l in lines:
        fields = l.replace('\n','').split(';')
        if fields[1]=="REFERENCIAS":
            break

        if fields[1]=="COMANDANTES":
            for k1 in range(1,len(fields)):
                lmonth = k1 - 3
                if not fields[k1]:
                    break
            f1 = True
            continue
        if not lmonth:
            continue
        if f1:
            if fields[1]:
                currentName = fields[1]
                if currentName!="COPILOTOS":
                    persons[currentName] = {}
                    k = 0
                    for i in range(1,lmonth+1):
                        persons[currentName][i] = []

        if currentName!="COPILOTOS":
            if currentName and k<4:
                for i in range(1,lmonth+1):
                    if fields[i+2]:
                        persons[currentName][i].append(fields[i+2])
        k += 1

        #if fields[1]=="COPILOTOS":
        #    break
    f.close()
    return persons

if __name__ == "__main__":

    importAircrewProgram()
