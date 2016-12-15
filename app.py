# coding: utf-8
from flask import Flask, json , render_template, request, Response, url_for, jsonify , session, redirect, current_app
from flask.views import View, MethodView
from urllib import quote_plus as urlencode
import requests
import xmltodict



app = Flask(__name__)

#Hämtar en lista över alla valkretsar i Sverige från Riksdagens API.
@app.route('/', methods =['GET'])
def index():
    #HTTP anrop till Riksdagens API för att hämta valkretsar
    response = requests.get('http://data.riksdagen.se/personlista/?termlista=valkrets')
    #Python behandlar XML fil som om den vore JSON
    valkretslista = xmltodict.parse(response.text)
    #lista med alla valkretsar
    tomlistavalkretsar = []
    for i in valkretslista['termlista']['term']:
        tomlistavalkretsar.append(i['namn'])
    #HTTP anrop till Riksdagens API för att hämta antal ledamöter på alla parti i Sverige (parti, namn , antal ) data till pie chart    
    response = requests.get('http://data.riksdagen.se/personlista/?termlista=parti')
    partilista = xmltodict.parse(response.text)
    
    allapartier = []
    for m in partilista['termlista']['term']:
        allapartier.append(m)
    #Returnerar alla valkretsar , partier  
    return render_template('index.html', kretsar = tomlistavalkretsar, partier = allapartier)

@app.route('/valkrets/<valkrets>', methods =['GET'])
def valkrets(valkrets):
    utfkod = urlencode(valkrets.encode('utf-8'))
    #HTTP anrop till Riksdagens API för att hämta alla partier i vald valkrets
    response = requests.get('http://data.riksdagen.se/personlista/?valkrets=' + utfkod) # json
    ledamot = xmltodict.parse(response.text)
    
    tomlistaledamot = []
    for d in ledamot['personlista']['person']:
        tomlistaledamot.append(d)
        
    response = requests.get('http://data.riksdagen.se/personlista/?valkrets='+utfkod+'&termlista=parti')
    kretspartilista = xmltodict.parse(response.text)
    
    kretsparti = []
    for n in kretspartilista['termlista']['term']:
        kretsparti.append(n)
    #Returnerar alla ledamöter och partier i vald valkrets
    return render_template('valkrets.html', ledamoter = tomlistaledamot, partier=kretsparti)

@app.route('/ledamot/<ledamot>', methods =['GET'])
def ledamot(ledamot):
    # hämta sorteringsnams och dela den till två olika [0] Fnamn och [1] Enamn
    fnamn = ledamot.split(',')[1]
    enamn = ledamot.split(',')[0]
    utfkodf = urlencode(fnamn.encode('utf-8'))
    utfkode = urlencode(enamn.encode('utf-8'))
    response = requests.get('http://data.riksdagen.se/personlista/?fnamn='+utfkodf+'&enamn='+utfkode)#json
    ledamotuppgift = xmltodict.parse(response.text)
    #All information om vald ledamot
    ledamot = ledamotuppgift['personlista']['person']
    email = ''
    title = ''
    #Vald information som skall visas
    for uppgift in ledamot['personuppgift']['uppgift']:
        if uppgift['kod']=="sv" and uppgift['typ'] =="titlar":
          title = uppgift['uppgift']

        if uppgift['kod']=="Officiell e-postadress" and uppgift['typ']=="eadress":
            email = uppgift['uppgift']
            
    #Returnerar information om vald ledamot
    return render_template('ledamot.html', ledamot=ledamot , email=email , title=title)

@app.route('/back/<valkrets>')	
def redirect_url(valkrets):
    return redirect (redirect_url (valkrets(valkrets)))

@app.route('/dokumentation')
def dokumentation():
    return render_template('dokumentation.html')

@app.route('/omoss')
def omoss():
    return render_template('omoss.html')

# Error handler for 404
@app.errorhandler(404)
def page_not_found(error):
    return render_template('404.html'), 404

# Error handler for 405
@app.errorhandler(405)
def method_not_allowed(error):
    return render_template('405.html'), 405


if __name__ == '__main__':
    app.debug = True
    app.run(port=2010)
