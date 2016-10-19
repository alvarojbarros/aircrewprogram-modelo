import time
from datetime import datetime,timedelta
import json

def now():
    return datetime.now()

def today():
    return now().date()

def errorLog(text):
    f = open('Error.log','a')
    line = "%s: %s\n" %(str(now()),text)
    f.write(line)
    f.close()


def checkMandatoryFields(obj):
    for field in obj.mandatoryFields():
        if not getattr(obj,field):
            errorLog('No se pudo inicializar %s, campo %s' % (obj,field))
            return False
    return True

def stringToDateTime(string):
    if not string:
        return None
    try:
        t = datetime.strptime(string, "%Y-%m-%d %H:%M:%S")
        return t
    except:
        return None

def stringToDate(string):
    if not string:
        return None
    try:
        t = datetime.strptime(string, "%Y-%m-%d")
        return t.date()
    except:
        return None

def stringToTime(string):
    if not string:
        return None
    try:
        t = datetime.strptime(string, "%H:%M:%S")
        return t.time()
    except:
        return None

def addTimeDaysToDatetime(days,myTime,myDatetime):
    seconds = myTime.hour * 3600 + myTime.minute * 60 + myTime.second
    try:
        myDatetime += timedelta(days,seconds)
    except:
        pass
    return myDatetime

def addTimeToDatetime(myTime,myDatetime):
    seconds = myTime.hour * 3600 + myTime.minute * 60 + myTime.second
    try:
        myDatetime += timedelta(0,seconds)
    except:
        pass
    return myDatetime

def addDaysToDatetime(days,myDatetime):
    try:
        myDatetime += timedelta(days,0)
    except:
        pass
    return myDatetime


def addDays(myDate, days):
    try:
        myDate += timedelta(days)
    except:
        pass
    return myDate

def addTime(myTime1, myTime2):
    # a ver si puede ser mas elegante y generico
    d1 = timedelta(hours=myTime1.hour,minutes = myTime1.minute,seconds=myTime1.second)
    d2 = timedelta(hours=myTime2.hour,minutes = myTime2.minute,seconds=myTime2.second)
    d3 = d1 + d2
    mins = d3.seconds // 60
    secs = d3.seconds % 60
    hrs = mins // 60
    mins = mins - hrs * 60
    myTime = time(hrs,mins,secs)
    return (myTime)


def importJson(filename):
    with open('datatest/%s.json' % filename, 'r') as fp:
        data = json.load(fp)
    return data


def getObjectClass(jsonlist,clasname,key=[]):
    if not key:
        records = []
    else:
        records = {}
    errors = False
    var = {}
    for e in jsonlist:
        exec('from %s import %s; r = %s(%s)' %(clasname,clasname,clasname,e),var)
        record = var['r']
        if not hasattr(record,'initOk'):
            errors = True
            break
        if not record.check():
            errors = True
            break
        if not key:
            records.append(record)
        else:
            keyvalues = [getattr(record,keyname,None) for keyname in key]
            records[tuple(keyvalues)] = record
    if errors:
        print("Hay Errores. Revisar Log")
        return False
    return records

def validateFieldsType(fieldsDefinition,fields):
    for key in fieldsDefinition:
        value = fields.get(key,None)
        if not value:
            continue
        if fieldsDefinition[key][0]=='str' and value.__class__.__name__!='str':
            errorLog('Error en Tipo de Dato %s %s' % (key,str(fields)))
            return False
        if fieldsDefinition[key][0]=='str' and len(value)>fieldsDefinition[key][1]:
            errorLog('Error en Longitud de campo %s %s' % (key,(str(fields))))
            return False
        if fieldsDefinition[key][0]=='int':
            try:
                v = int(value)
            except:
                errorLog('Error en Tipo de Dato %s %s' % (key,(str(fields))))
                return False
        if fieldsDefinition[key][0]=='float':
            try:
                v = float(value)
            except:
                errorLog('Error en Tipo de Dato %s %s' % (key,(str(fields))))
                return False
        if fieldsDefinition[key][0]=='time':
            try:
                v = datetime.strptime(value, "%H:%M:%S")
            except:
                errorLog('Error en Tipo de Dato %s %s' % (key,(str(fields))))
                return False
        if fieldsDefinition[key][0]=='date':
            try:
                v = datetime.strptime(string, "%Y-%m-%d")
            except:
                errorLog('Error en Tipo de Dato %s %s' % (key,(str(fields))))
                return False
        if fieldsDefinition[key][0]=='datetime':
            try:
                v = datetime.strptime(string, "%Y-%m-%d %H:%M:%S")
            except:
                errorLog('Error en Tipo de Dato %s %s' % (key,(str(fields))))
                return False

    return True
