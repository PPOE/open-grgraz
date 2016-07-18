import os
import json
import csv
import requests
from requests_ntlm import HttpNtlmAuth

def createSession():
    print('createSession')


def downloadMotionLists():
    print('downloadMotionLists')
    #session = requests.Session()
    #session.auth = HttpNtlmAuth('...', '...', session)
    #r = session.get('https://magistrat.graz.at')

    ###############

    #session = requests.Session()
    #r = session.get(
    #    'https://magistrat.graz.at/secure/Gemeinderat/IA/_layouts/15/inplview.aspx?List={90DB24AA-D64E-49BF-A001-4C7652309546}&View={9E32B935-7592-4E95-9117-3B5A9D91F08D}&ViewCount=2&IsXslView=TRUE&IsCSR=TRUE&GroupString=%3B%232016%3B%2320160616%3B%23&IsGroupRender=TRUE&WebPartID={9E32B935-7592-4E95-9117-3B5A9D91F08D}',
    #    cookies={'...': '...'}
    #)


def parseMotionLists():
    print('parseMotionLists')

    jsonFiles = os.listdir('files/jsonMotionLists/')
    jsonFiles = filter(lambda name: name.endswith('.json'), jsonFiles)

    motionLists = []
    for jsonFile in jsonFiles:
        with open('files/jsonMotionLists/motion-list-sample.json') as jsonFile:
            motionLists.append(json.load(jsonFile))

    motionsCsv = []
    for motionList in motionLists:
        for motion in motionList['Row']:
            motionsCsv.append([
                motion['Sitzung_x0020_am'],
                motion['ID'],
                motion['Title'],
                motion['Dokumentenart']['Label'],
                motion['Antragsteller'][0]['title'],
                motion['Fraktion'],
                motion['Betreff'],
                '',
                motion['FileRef'],
                motion['FileLeafRef'],
            ])

    with open('files/motion-list-sample.csv', 'w', newline='') as csvFile:
        writer = csv.writer(csvFile)
        writer.writerow( ('Datum', 'Nummer', 'Titel', 'Art', 'Antragsteller', 'Partei', 'Dringlichkeit', 'Angenommen', 'Link', 'Anwort 1', 'Anwort 2', 'Antwort', 'link') )
        writer.writerows(motionsCsv)


def downloadMotions():
    print('downloadMotions')


createSession()
downloadMotionLists()
parseMotionLists()
downloadMotions()
