import os
import json
import csv
import requests
from requests_ntlm import HttpNtlmAuth

def createSession():
    print('createSession')
    session = requests.Session()
    session.auth = HttpNtlmAuth('\\username', 'password', session)
    r = session.get('https://magistrat.graz.at')
    print(r)
    return session


def downloadMotionLists():
    print('downloadMotionLists')


def parseMotionLists():
    print('parseMotionLists')

    jsonFiles = os.listdir('files/jsonMotionLists/')
    jsonFiles = filter(lambda name: name.endswith('.json'), jsonFiles)

    motionLists = []
    for jsonFile in jsonFiles:
        with open('files/jsonMotionLists/' + jsonFile) as jsonFile:
            motionLists.append(json.load(jsonFile))

    motionsCsv = []
    for motionList in motionLists:
        for motion in motionList['Row']:
            motionsCsv.append([
                motion['Sitzung_x0020_am'],
                motion['ID'],
                motion['Title'],
                motion['Dokumentenart']['Label'],
                motion['Antragsteller'][0]['jobTitle'] + ' ' + motion['Antragsteller'][0]['title'],
                motion['Fraktion'],
                motion['Betreff'],
                '',
                motion['FileRef'],
                motion['FileLeafRef'],
            ])

    # todo: fix sort
    def customSort(motion):
        date = motion[0].split('.')
        return (date[2], date[2], date[1], motion[1])

    motionsCsv = sorted(motionsCsv, key=customSort)

    with open('files/motions.csv', 'w', newline='') as csvFile:
        writer = csv.writer(csvFile)
        writer.writerow( ('Datum', 'Nummer', 'Titel', 'Art', 'Antragsteller', 'Partei', 'Dringlichkeit', 'Angenommen', 'Link', 'Anwort 1', 'Anwort 2', 'Antwort', 'link') )
        writer.writerows(motionsCsv)

    return motionsCsv


def downloadMotions(motionsCsv, session):
    print('downloadMotions')
    i = 0
    for motion in motionsCsv:
        url = 'https://magistrat.graz.at' + motion[8]
        print('%4d - downloading: %s' % (i, url))
        i += 1
        local_filename = url.split('/')[-1]
        # NOTE the stream=True parameter
        r = session.get(url, stream=True)
        with open('files/motions/' + local_filename, 'wb') as f:
            for chunk in r.iter_content(chunk_size=1024):
                if chunk: # filter out keep-alive new chunks
                    f.write(chunk)
                    #f.flush() commented by recommendation from J.F.Sebastian


session = createSession()
downloadMotionLists()
motionsCsv = parseMotionLists()
downloadMotions(motionsCsv, session)
