import Tools
from AircraftMovement import AircraftMovement
from LineProgram import LineProgram
import json
import datetime

days = ['LUNES','MARTES','MIERCOLES','JUEVES','VIERNES','SABADO','DOMINGO']

def importAircrewProgram():

    f = open('datatest/tripulacion.Octubre 2_3.csv','r')
    f1 = False
    persons = {}
    currentName = None
    k = 0
    for l in f:
        fields = l.replace('\n','').split(';')
        if fields[1]=="COMANDANTES":
            f1 = True
            continue
        if f1:
            if fields[1]:
                currentName = fields[1]
                persons[currentName] = {}
                k = 0
                for i in range(1,32):
                    persons[currentName][i] = []

        if currentName and k<4:
            for i in range(1,32):
                if fields[i+2]:
                    persons[currentName][i].append(fields[i+2])
        k += 1

        if fields[1]=="COPILOTOS":
            break
    f.close()
    return persons
    print(persons['PASCUAL'])

if __name__ == "__main__":

    importAircrewProgram()