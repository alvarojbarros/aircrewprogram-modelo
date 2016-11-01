import time
from datetime import datetime,timedelta
import json
import copy
from AircraftMovement import AircraftMovement
from Flight import Flight

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
    seconds = 0
    if myTime:
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

def addMonthToDateTime(months,myDateTime):
    newmonth = ((( myDateTime.month - 1) + months ) % 12 ) + 1
    newyear  = myDateTime.year + ((( myDateTime.month - 1) + months ) / 12 )
    newday = myDateTime.day
    if newday>=28:
        while newday >= 28:
            try:
                res = datetime( int(newyear), int(newmonth), newday)
                return res
            except:
                newday += -1
    else:
        res = datetime( int(newyear), int(newmonth), newday)
    return res

def firstDayOfMonth(myDateTime):
    return datetime(myDateTime.year,myDateTime.month,1)

def lastDayOfMonth(myDateTime):
    firstDate = datetime(myDateTime.year,myDateTime.month,1)
    lastDate = addDaysToDatetime(-1,addMonthToDateTime(1,firstDate))
    return lastDate

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

def addHoursToDateTime(myDate, h):
    try:
        myDate += timedelta(hours=h)
    except:
        pass
    return myDate

def addMinutesToDateTime(myDate, m):
    try:
        myDate += timedelta(minutes=m)
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
    with open(filename, 'r') as fp:
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
            #break
        if not record.check():
            errors = True
            #break
        if not key:
            records.append(record)
        else:
            keyvalues = [getattr(record,keyname,None) for keyname in key]
            records[tuple(keyvalues)] = record
    if errors:
        print("Hay Errores. Revisar Log")
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

def toJson(obj,f):
    newobj = copy.copy(obj)
    #if obj.__class__.__name__==

    for field in obj.fieldsDefinition():
        value = getattr(newobj,field)
        #if value.__class__.__name__ in ('AircraftMovement','dict','list'):
        #    if value:
        #        nvalue = toJson(value,f)
        #        setattr(newobj,field,nvalue)
        if value.__class__.__name__=='datetime':
            value = getattr(newobj,field)
            if value:
                setattr(newobj,field,str(value))
        '''elif value.__class__.__name__=='dict':
            dic = getattr(newobj,field)
            for key in dic:
                dic[key] = dic[key].__dict__
            f.write('%s: %s\n' %(field,dic))
        elif value.__class__.__name__=='list':
            listv = getattr(newobj,field)
            for i in range(len(listv)):
                listv[i] = listv[i].__dict__ '''
    return newobj

def json_serial(obj):
    """JSON serializer for objects not serializable by default json code"""

    #print((obj,obj.__class__.__name__))
    if obj.__class__.__name__=='date':
        serial = str(obj)
        return serial
    if obj.__class__.__name__=='time':
        serial = str(obj)
        return serial
    if isinstance(obj, int):
        serial = str(obj)
        return serial
    if isinstance(obj, datetime):
        serial = obj.isoformat()
        return serial
    if isinstance(obj, timedelta):
        serial = str(obj)
        return serial
    #if isinstance(obj, list):
    #    serial = json.dumps(obj,default=json_serial, sort_keys=True,indent=4, separators=(',', ': '))
    #    return serial
    if isinstance(obj, AircraftMovement):
        serial = json.dumps(obj.__dict__,default=json_serial)
        serial = eval(serial.replace('null','None').replace('true','True'))
        return serial
    if isinstance(obj, Flight):
        serial = json.dumps(obj.__dict__,default=json_serial)
        serial = eval(serial.replace('null','None').replace('true','True'))
        return serial
    raise TypeError ("Type not serializable")


def importTable(filename):
    f = open(filename, 'r')
    k = 0
    res = {}
    for l in f:
        fields = l.replace('\n','').split('\t')
        if k==0:
            dkeys = fields
        else:
            dic = {}
            for i in range(1,len(fields)):
                dic[dkeys[i]] = int(fields[i])
            res[(int(fields[1]),int(fields[13]))] = dic
        k += 1
    return res

def timeDiff(st,et):
    t1 = datetime(1900,1,1,st.hour,st.minute,st.second)
    t2 = datetime(1900,1,1,et.hour,et.minute,et.second)
    return t2-t1
