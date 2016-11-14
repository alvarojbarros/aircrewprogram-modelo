import os
from flask import Flask, render_template, request, redirect
from werkzeug.utils import secure_filename
from CheckAircrewProgram import *
UPLOAD_FOLDER = './tmp/'

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


@app.route('/', methods=['GET', 'POST'])
def index():

    if request.method == 'POST':
        vuelos = request.files['file1']
        if vuelos.filename == '':
            return 'No selected file'
            #return redirect(request.url)
        tripu = request.files['file2']
        if tripu.filename == '':
            return 'No selected file'
            #return redirect(request.url)
        if vuelos and tripu:
            res = process(vuelos,tripu)
            if res:
                return render_template('ShowErrors.html',ErrorList=res)
            return "No hay Errores"

        #if vuelos:
        #    tripu = ""
        #    res = process(vuelos,tripu)
        #    return render_template('Vuelos.html',Vuelos=res)

    return render_template('upload.html')

@app.context_processor
def utility_processor():
    def sortDict(myDict):
        return sorted(myDict)
    def getFlightsByDate(myDict):
        dic = {}
        for fn in myDict:
            d = myDict[fn].StartDateTime.date()
            if not d in dic:
                dic[d] = []
            dic[d].append(myDict[fn])
        return dic
    def getFlightsSorted(flights):
        flights.sort(key=lambda x: x.StartDateTime)
        newList = []
        for flight in flights:
            newList.append('%s-%s-%s' %(flight.Origin,flight.FlightNumber,flight.Destination))
        return ' / '.join(newList)

    def getDaysList(Vuelos):
        list = []
        for aircraft in Vuelos:
            for flight in Vuelos[aircraft].Flights:
                myFlight = Vuelos[aircraft].Flights[flight]
                if myFlight.StartDate not in list:
                    list.append(myFlight.StartDate)
        return sorted(list)
    def getVuelosAircraft(Vuelos,date):
        list = []
        for vuelo in Vuelos:
            myVuelo = Vuelos[vuelo]
            if myVuelo.StartDate==date:
                list.append(myVuelo)
        list.sort(key=lambda x: x.StartDateTime)
        return list
    return dict(sortDict=sortDict \
        ,getFlightsByDate=getFlightsByDate  \
        ,getFlightsSorted=getFlightsSorted  \
        ,getDaysList=getDaysList \
        ,getVuelosAircraft=getVuelosAircraft \
        )

if __name__ == "__main__":
    app.run()