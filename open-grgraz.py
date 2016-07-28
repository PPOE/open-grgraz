import sys
import os
import json
import csv
import requests
from requests_ntlm import HttpNtlmAuth
import olefile
from shutil import copyfile
import glob
import open_grgraz.wsgi
import api
from api.models import *
import datetime

BASE_URL = 'https://magistrat.graz.at'
FILES_PATH = 'files/'
MOTION_LISTS_PATH = FILES_PATH + 'motionLists/'
ANSWER_LISTS_PATH = FILES_PATH + 'answerLists/'
RAW_MOTIONS_PATH = FILES_PATH + 'motionsRaw/'
RAW_ANSWERS_PATH = FILES_PATH + 'answersRaw/'
MOTIONS_PATH = FILES_PATH + 'motions/'
ANSWERS_PATH = FILES_PATH + 'answers/'


def create_session(username, password):
    session = requests.Session()
    session.auth = HttpNtlmAuth('\\' + username, password)
    result = session.get(BASE_URL)
    if result.status_code != 200:
        sys.exit('Login error {}.'.format(result.status_code))
    return session


def download_motion_lists(session):
    print('download_motion_lists')


def download_answer_lists(session):
    print('download_answer_lists')


def parse_lists(lists_path, csv_filename):
    json_files = glob.glob(lists_path + '*.json')

    element_lists = []
    for file_path in json_files:
        with open(file_path, 'r') as file:
            element_lists.append(json.load(file))

    element_csv = []
    for element_list in element_lists:
        for element in element_list['Row']:

            if 'Polz Wolfgang' == element['Antragsteller'][0]['title']:
                continue

            session_date = datetime.datetime.strptime(element['Sitzung_x0020_am'], '%d.%m.%Y')
            session = ParliamentarySession.objects.update_or_create(session_date=session_date)[0]
            #print(session)

            group_id = element['Fraktion']
            group = ParliamentaryGroup.objects.update_or_create(id=group_id, name=group_id)[0]
            #print(group)

            person_name = element['Antragsteller'][0]['title']
            person_academic_degree = element['Antragsteller'][0]['jobTitle']
            person_email = element['Antragsteller'][0]['email']
            person = CouncilPerson.objects.update_or_create(name=person_name,
                                                         academic_degree=person_academic_degree,
                                                         email=person_email,
                                                         parliamentary_group=group)[0]

            #print(person)

            motion_type = element['Dokumentenart']['Label']
            motion_id = int(float(element['FileLeafRef'][:4].replace('_', '')))
            print(motion_id)
            if motion_type == 'GR-Antwort':
                answer = Answer.objects.update_or_create(id=element['ID'], motion_id=motion_id,
                                                         session=session, title=element['Title'],
                                                         parliamentary_group=group, proposer=person)[0]
                #print(answer)
            else:
                from django.core.exceptions import ObjectDoesNotExist
                try:
                    answers = Answer.objects.filter(motion_id=motion_id)
                except ObjectDoesNotExist:
                    answers = None
                motion = Motion.objects.update_or_create(id=element['ID'], motion_id=motion_id,
                                                         session=session, title=element['Title'],
                                                         motion_type=motion_type, parliamentary_group=group,
                                                         proposer=person)[0]
                motion.answers.set(answers)
                motion.save()
                #print(motion)


            element_csv.append([
                element['Sitzung_x0020_am'],
                element['ID'],
                element['Title'],
                element['Dokumentenart']['Label'],
                element['Antragsteller'][0]['jobTitle'] + ' ' + element['Antragsteller'][0]['title'],
                element['Fraktion'],
                element['Betreff'],
                '',
                element['FileRef'],
                element['FileLeafRef'],
            ])

    def element_sort(answer):
        date = answer[0].split('.')
        return date[2], date[2], date[1], int(answer[1])

    element_csv = sorted(element_csv, key=element_sort)

    with open(FILES_PATH + csv_filename, 'w', newline='') as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow(('Datum', 'Nummer', 'Titel', 'Art', 'Antragsteller', 'Partei', 'Dringlichkeit', 'Angenommen', 'Link', 'Anwort 1', 'Anwort 2', 'Antwort', 'link'))
        writer.writerows(element_csv)

    return element_csv


def download_from_csv(csv, base_path, session):
    download_number = 1
    for line in csv:
        url = BASE_URL + line[8]
        local_filename = url.split('/')[-1]

        if os.path.exists(base_path + local_filename):
            continue

        print('{:>4} - downloading: {}'.format(download_number, local_filename))
        download_number += 1
        result = session.get(url, stream=True)
        with open(base_path + local_filename, 'wb') as file:
            for chunk in result.iter_content(chunk_size=1024):
                if chunk:
                    file.write(chunk)


def copy_files(source_path, destination_path, pattern):
    file_paths = glob.glob(source_path + pattern)
    for file_path in file_paths:
        filename = file_path.split('/')[-1]
        copyfile(file_path, destination_path + filename)


def convert_documents(motions_csv):
    for motion in motions_csv:
        filename = motion[9]
        if filename.split('.')[-1] == 'msg' or filename.split('.')[-1] == 'pdf':
            continue

        #todo
        #unoconv


def extract_email_attachments(read_base_path, write_base_path, motions_csv):
    for motion in motions_csv:
        filename = motion[9]
        if filename.split('.')[-1] != 'msg':
            continue
        file_path = read_base_path + filename

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
            if not os.path.exists(write_base_path + dirname):
               os.makedirs(write_base_path + dirname)

            for dir in attachment_dirs:
                long_filename = get_stream(ole, dir + '/__substg1.0_3707')
                short_filename = get_stream(ole, dir + '/__substg1.0_3704')

                data = None
                if ole.exists(dir + '/__substg1.0_37010102'):
                    data = ole.openstream(dir + '/__substg1.0_37010102').read()

                attachment_filename = short_filename
                if attachment_filename is None:
                    attachment_filename = long_filename

                if attachment_filename == 'image001.jpg':
                    continue

                if attachment_filename is not None and data is not None:
                    attachment_path = write_base_path + dirname + '/' + attachment_filename
                    if not os.path.exists(attachment_path):
                        file = open(attachment_path, 'wb')
                        file.write(data)
                        file.close()



def main(username, password):
    session = create_session(username, password)
    
    download_motion_lists(session)  # this does nothing for now.
    download_answer_lists(session)  # this does nothing for now.

    answers_csv = parse_lists(ANSWER_LISTS_PATH, 'answers.csv')
    motions_csv = parse_lists(MOTION_LISTS_PATH, 'motions.csv')
    
    download_from_csv(answers_csv, RAW_ANSWERS_PATH, session)
    download_from_csv(motions_csv, RAW_MOTIONS_PATH, session)

    copy_files(RAW_ANSWERS_PATH, ANSWERS_PATH, '*.pdf')
    copy_files(RAW_MOTIONS_PATH, MOTIONS_PATH, '*.pdf')

    convert_documents(motions_csv)

    extract_email_attachments(RAW_ANSWERS_PATH, ANSWERS_PATH, answers_csv)
    extract_email_attachments(RAW_MOTIONS_PATH, MOTIONS_PATH, motions_csv)

    # todo:
    #  - fetch motions and answer lists
    #  - create pdfs out of word documents,
    #  - ocr pdfs without text
    #  - create webfrontend


if __name__ == '__main__':
    if len(sys.argv) < 3:
        sys.exit('No username and password set.')
    main(sys.argv[1], sys.argv[2])
