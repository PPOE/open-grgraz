import sys
import os
import json
import csv
import requests
from requests_ntlm import HttpNtlmAuth
import olefile

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

def extract_email_attachments(motions_csv):
    for motion in motions_csv:
        filename = motion[9]
        if filename.split('.')[-1] != 'msg':
            continue
        print('open: ' + filename)
        file_path = RAW_MOTIONS_PATH + filename
        #msg = email.message_from_file(open(file_path, mode='r', encoding='utf-8', errors='replace'))

        ole = olefile.OleFileIO(file_path)

        attachment_dirs = []
        for dir in ole.listdir():
            if dir[0].startswith('__attach') and dir[0] not in attachment_dirs:
                attachment_dirs.append(dir[0])

        def windowsUnicode(string):
            if string is None:
                return None
            if sys.version_info[0] >= 3:  # Python 3
                return str(string, 'utf_16_le')
            #else:  # Python 2
            #    return unicode(string, 'utf_16_le')

        def get_stream(ole, filename):
            asciiVersion = None
            unicodeVersion = None

            if ole.exists(filename + '001E'):
                asciiVersion = ole.openstream(filename + '001E').read()

            if ole.exists(filename + '001F'):
                unicodeVersion = windowsUnicode(ole.openstream(filename + '001F').read())

            if asciiVersion is None:
                return unicodeVersion
            elif unicodeVersion is None:
                return asciiVersion
            else:
                return unicodeVersion

        if len(attachment_dirs) > 0:
            dirname = filename.split('.')[0]
            if not os.path.exists(MOTIONS_PATH + dirname):
               os.makedirs(MOTIONS_PATH + dirname)

            for dir in attachment_dirs:
                long_filename = get_stream(ole, dir + '/__substg1.0_3707')
                short_filename = get_stream(ole, dir + '/__substg1.0_3704')

                data = None
                if ole.exists(dir + '/__substg1.0_37010102'):
                    data = ole.openstream(dir + '/__substg1.0_37010102').read()

                attachment_filename = long_filename
                if attachment_filename is None:
                    attachment_filename = short_filename

                #print(attachment_filename)
                #print(data)

                if attachment_filename == 'image001.jpg':
                    continue

                if attachment_filename is not None and data is not None:
                    print('save: ' + attachment_filename)
                    attachment_path = MOTIONS_PATH + dirname + '/' + attachment_filename
                    if not os.path.exists(attachment_path):
                        file = open(attachment_path, 'wb')
                        file.write(data)
                        file.close()


def main(username, password):
    session = create_session(username, password)
    download_motion_lists(session)
    motions_csv = parse_motion_lists()
    download_motions(motions_csv, session)
    extract_email_attachments(motions_csv)

    # todo:
    #  - create pdfs out of word documents,
    #  - ocr pdfs without text
    #  - fetch answers
    #  - match motions and answers


if __name__ == '__main__':
    if len(sys.argv) < 3:
        sys.exit('No username and password set.')
    main(sys.argv[1], sys.argv[2])
