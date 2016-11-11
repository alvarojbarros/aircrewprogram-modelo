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
            flash('No selected file')
            return redirect(request.url)
        tripu = request.files['file2']
        if tripu.filename == '':
            flash('No selected file')
            return redirect(request.url)

        if vuelos and tripu:
            res = test(vuelos,tripu)
            if res:
                return render_template('ShowErrors.html',ErrorList=res)
            return "No hay Errores"
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
    return dict(sortDict=sortDict,getFlightsByDate=getFlightsByDate,getFlightsSorted=getFlightsSorted)

if __name__ == "__main__":
    app.run()