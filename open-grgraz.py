import sys
import os
import json
import csv
import requests
from requests_ntlm import HttpNtlmAuth

BASE_URL = 'https://magistrat.graz.at'
FILES_PATH = 'files/'
MOTION_LISTS_PATH = FILES_PATH + 'motionLists/'
RAW_MOTIONS_PATH = FILES_PATH + 'rawMotions/'
MOTIONS_PATH = FILES_PATH + 'motions/'


def create_session(username, password):
    session = requests.Session()
    session.auth = HttpNtlmAuth('\\' + username, password)
    result = session.get(BASE_URL)
    if result.status_code != 200:
        sys.exit('Login error {}.'.format(result.status_code))
    return session


def download_motion_lists(session):
    print('downloadMotionLists')


def parse_motion_lists():
    json_files = os.listdir(MOTION_LISTS_PATH)
    json_files = filter(lambda name: name.endswith('.json'), json_files)

    motion_lists = []
    for file_name in json_files:
        with open(MOTION_LISTS_PATH + file_name) as file:
            motion_lists.append(json.load(file))

    motions_csv = []
    for motionList in motion_lists:
        for motion in motionList['Row']:
            motions_csv.append([
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

    def motion_sort(motion):
        date = motion[0].split('.')
        return date[2], date[2], date[1], motion[1]

    motions_csv = sorted(motions_csv, key=motion_sort)

    with open(FILES_PATH + 'motions.csv', 'w', newline='') as csvFile:
        writer = csv.writer(csvFile)
        writer.writerow(('Datum', 'Nummer', 'Titel', 'Art', 'Antragsteller', 'Partei', 'Dringlichkeit', 'Angenommen', 'Link', 'Anwort 1', 'Anwort 2', 'Antwort', 'link'))
        writer.writerows(motions_csv)

    return motions_csv


def download_motions(motions_csv, session):
    download_number = 1
    for motion in motions_csv:
        url = BASE_URL + motion[8]
        local_filename = url.split('/')[-1]

        if os.path.exists(RAW_MOTIONS_PATH + local_filename):
            continue

        print('{:>4} - downloading: {}'.format(download_number, local_filename))
        download_number += 1
        result = session.get(url, stream=True)
        with open(RAW_MOTIONS_PATH + local_filename, 'wb') as file:
            for chunk in result.iter_content(chunk_size=1024):
                if chunk:
                    file.write(chunk)


def main(username, password):
    session = create_session(username, password)
    download_motion_lists(session)
    motions_csv = parse_motion_lists()
    download_motions(motions_csv, session)


if __name__ == '__main__':
    if len(sys.argv) < 3:
        sys.exit('No username and password set.')
    main(sys.argv[1], sys.argv[2])
